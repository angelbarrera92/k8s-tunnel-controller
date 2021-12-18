import subprocess

from kopf.testing import KopfRunner


def test_controller():
    with KopfRunner(
        ["run", "-A", "--liveness=http://0.0.0.0:8080/healthz", "controller.py"]
    ) as runner:
        # do something while the operator is running.

        subprocess.run(
            "kubectl apply -f hack/deployments/example/nginx.yaml",
            shell=True,
            check=True,
        )

    assert runner.exit_code == 0
    assert runner.exception is None
    assert (
        "new service (default/nginx) listened with the k8s-tunnel-controller/tunnel annotation"
        in runner.stdout
    )
    assert "creating tunnel secret for service default/nginx" in runner.stdout
    assert "creating tunnel configmap for service default/nginx" in runner.stdout
    assert "creating tunnel pod for service default/nginx" in runner.stdout


def test_annotations():
    with KopfRunner(
        ["run", "-A", "--liveness=http://0.0.0.0:8080/healthz", "controller.py"]
    ) as runner:
        subprocess.run(
            "kubectl annotate svc nginx-default k8s-tunnel-controller/tunnel=nginx-2",
            shell=True,
            check=True,
        )

    assert runner.exit_code == 0
    assert runner.exception is None
    assert "update service default/nginx-default annotations" in runner.stdout
    assert "creating tunnel secret for service default/nginx-default" in runner.stdout
    assert (
        "creating tunnel configmap for service default/nginx-default" in runner.stdout
    )
    assert "creating tunnel pod for service default/nginx-default" in runner.stdout
