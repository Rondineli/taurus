resource "kubernetes_ingress" "taurus_ingress" {
  metadata {
    name = "taurus-ingress"
  }

  spec {
    backend {
      service_name = "MyApp1"
      service_port = 8080
    }

    rule {
      http {
        path {
          backend {
            service_name = "taurus-svc"
            service_port = 8080
          }

          path = "/api/*"
        }
      }
    }

    tls {
      secret_name = "tls-secret"
    }
  }
}

resource "kubernetes_pod" "nginx" {
  metadata {
    name = "nginx"
    labels = {
      app = "MyApp1"
    }
  }

  spec {
    container {
      image = "nginx:1.7.9"
      name  = "nginx"

      port {
        container_port = 8080
      }
    }
  }
}

resource "kubernetes_pod" "taurus" {
  metadata {
    name = "taurus"
    labels = {
      app = "taurus"
    }
  }

  spec {
    container {
      image = "taurus"
      name  = "taurus"

      port {
        container_port = 8080
      }
    }
  }