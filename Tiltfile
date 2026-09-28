# Tiltfile for demo-app.
#
# Deploys with the same Helm chart ArgoCD uses, so local development and
# production render from one source of truth.
#
#   tilt up   interactive watch loop, from a workstation
#   tilt ci   one-shot: build, deploy, wait for green, exit. Use in agents/CI.
#
# Two build modes, chosen automatically:
#
#   laptop     docker builds locally and pushes to the in-cluster registry
#              through a port-forward. Requires, in another terminal:
#                kubectl port-forward -n build svc/registry 5000:5000
#
#   in-cluster set BUILDER=buildkit. Builds with buildkitd inside the cluster,
#              no docker socket needed. This is what the remote-dev agent uses.

NAMESPACE = os.getenv('TILT_NAMESPACE', 'dev-sandbox')
BUILDER = os.getenv('BUILDER', 'local')
BUILDKIT_ADDR = os.getenv('BUILDKIT_ADDR', 'tcp://buildkitd.build.svc:1234')
CLUSTER_REGISTRY = 'registry.build.svc:5000'

allow_k8s_contexts('kind-dev')

if BUILDER == 'buildkit':
    IMAGE = CLUSTER_REGISTRY + '/demo-app'
    custom_build(
        IMAGE,
        'buildctl --addr ' + BUILDKIT_ADDR + ' build ' +
        '  --frontend dockerfile.v0 ' +
        '  --local context=app --local dockerfile=app ' +
        '  --output type=image,name=$EXPECTED_REF,push=true,registry.insecure=true',
        deps=['app'],
        skips_local_docker=True,
    )
else:
    # Push to localhost:5000 (port-forward), but rewrite the image reference in
    # the manifests to the name the cluster nodes can actually resolve.
    default_registry('127.0.0.1:5000', host_from_cluster=CLUSTER_REGISTRY)
    IMAGE = 'demo-app'
    docker_build(IMAGE, 'app')

load('ext://namespace', 'namespace_create')
namespace_create(NAMESPACE)
k8s_yaml(helm(
    'app/chart',
    name='demo-app',
    namespace=NAMESPACE,
    set=['image.repository=' + IMAGE, 'image.pullPolicy=Always', 'replicaCount=1'],
))
k8s_resource('demo-app', port_forwards='8100:8080', labels=['app'])
