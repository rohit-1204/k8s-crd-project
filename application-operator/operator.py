import kopf
from kubernetes import client, config


# Kubernetes cluster configuration
config.load_incluster_config()


@kopf.on.create(
    "platform.example.com",
    "v1",
    "applications"
)
def create_application(spec, name, namespace, **kwargs):

    image = spec["image"]
    replicas = spec["replicas"]
    port = spec["port"]

    apps_api = client.AppsV1Api()
    core_api = client.CoreV1Api()

    # -------------------------
    # Deployment
    # -------------------------

    deployment = client.V1Deployment(

        metadata=client.V1ObjectMeta(
            name=name,
            namespace=namespace
        ),

        spec=client.V1DeploymentSpec(

            replicas=replicas,

            selector=client.V1LabelSelector(
                match_labels={
                    "app": name
                }
            ),

            template=client.V1PodTemplateSpec(

                metadata=client.V1ObjectMeta(
                    labels={
                        "app": name
                    }
                ),

                spec=client.V1PodSpec(

                    containers=[
                        client.V1Container(

                            name=name,

                            image=image,

                            ports=[
                                client.V1ContainerPort(
                                    container_port=port
                                )
                            ]
                        )
                    ]
                )
            )
        )
    )

    apps_api.create_namespaced_deployment(
        namespace=namespace,
        body=deployment
    )

    # -------------------------
    # Service
    # -------------------------

    service = client.V1Service(

        metadata=client.V1ObjectMeta(
            name=name,
            namespace=namespace
        ),

        spec=client.V1ServiceSpec(

            selector={
                "app": name
            },

            ports=[
                client.V1ServicePort(
                    port=port,
                    target_port=port
                )
            ],

            type="ClusterIP"
        )
    )

    core_api.create_namespaced_service(
        namespace=namespace,
        body=service
    )

    print(
        f"Application {name} created successfully"
    )