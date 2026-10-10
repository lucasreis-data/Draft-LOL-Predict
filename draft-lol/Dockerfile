# ---------- build ----------
FROM maven:3.9-eclipse-temurin-17 AS build
WORKDIR /build

# Camada de dependencias separada: so refaz o download se o pom.xml mudar.
COPY pom.xml .
RUN mvn -B -q dependency:go-offline

COPY src ./src
RUN mvn -B -q -DskipTests package \
 && cp target/*.jar /build/app.jar

# ---------- runtime ----------
FROM eclipse-temurin:17-jre
WORKDIR /app

RUN useradd -r -u 1001 -m app
COPY --from=build --chown=app:app /build/app.jar app.jar
USER app

# Tarefa Fargate do Java tem 2 GB: deixa 75% para o heap e o resto para metaspace/threads.
ENV JAVA_OPTS="-XX:MaxRAMPercentage=75 -XX:+ExitOnOutOfMemoryError" \
    PYTHON_API_URL="http://localhost:5000"

EXPOSE 8080

# Sem HEALTHCHECK aqui: a saude e checada pelo ALB em /Testar (ver infra).
ENTRYPOINT ["sh", "-c", "exec java $JAVA_OPTS -jar app.jar"]
