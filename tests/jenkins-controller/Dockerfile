FROM jenkins/jenkins:lts

ENV \
  CASC_JENKINS_CONFIG=/usr/share/jenkins/ref/casc_configs \
  JENKINS_REF=/usr/share/jenkins/ref

ARG PLUGINS_FILE=plugins-rolling.txt
COPY $PLUGINS_FILE $JENKINS_REF/plugins.txt
RUN /usr/local/bin/install-plugins.sh < $JENKINS_REF/plugins.txt

COPY --chown=jenkins log.properties $JENKINS_REF/log.properties
ENV JAVA_OPTS -Dorg.eclipse.jetty.server.Request.maxFormContentSize=100000000 \
 			  -Djenkins.install.runSetupWizard=false \
			  -Djava.util.logging.config.file=$JENKINS_REF/log.properties

COPY bin/* /usr/bin/
ENTRYPOINT ["/usr/bin/docker-entrypoint"]

# jenkins configuration-as-code
COPY --chown=jenkins config $JENKINS_REF/config.dist
RUN mv $JENKINS_REF/config.dist/common $CASC_JENKINS_CONFIG
