# Tiltfile for demo-app.
#
# Builds the image with buildkit (in-cluster, no docker socket required) and
# deploys it with the same Helm chart ArgoCD uses, so local development and
# production render from one source of truth.
#
#   tilt ci   one-shot: build, deploy, wait for green, exit. Use this in agents/CI.
#   tilt up   interactive watch loop. Use this at a workstation.

REGISTRY = os.getenv('REGISTRY', 'registry.build.svc:5000')
NAMESPACE = os.getenv('TILT_NAMESPACE', 'dev-sandbox')
IMAGE = REGISTRY + '/demo-app'

custom_build(
    IMAGE,
    'buildctl --addr tcp://buildkitd.build.svc:1234 build ' +
    '  --frontend dockerfile.v0 ' +
    '  --local context=app --local dockerfile=app ' +
    '  --output type=image,name=$EXPECTED_REF,push=true,registry.insecure=true',
    deps=['app'],
    skips_local_docker=True,
)

k8s_yaml(namespace_yaml(NAMESPACE))
k8s_yaml(helm(
    'app/chart',
    name='demo-app',
    namespace=NAMESPACE,
    set=['image.repository=' + IMAGE, 'image.pullPolicy=Always', 'replicaCount=1'],
))
k8s_resource('demo-app', port_forwards='8100:8080', labels=['app'])
