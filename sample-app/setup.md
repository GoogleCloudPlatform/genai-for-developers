
# Java application development using a Maven repository
Last Updated: 2024-01-31
When developing a Java application for IBM® MQ, by using a Maven repository to automatically install dependencies, you do not need to explicitly install anything before using IBM MQ interfaces.

# Maven Central Repository
Maven is a tool for building applications and also provides a repository for holding artifacts that your application may want to access.

The Maven Repository (or Central Repository) has a structure that allows files such as JAR files to have distinct versions that are then easily discovered with a well-known naming mechanism. Build tools can then use those names to dynamically pull in the dependencies for your application. In the definition of your application, which, when using Maven as a build tool, is called the POM file, you just name the dependencies and the build process knows what to do from there.

# IBM MQ client files
Copies of the IBM MQ Java client interfaces are available in the Central Repository under the com.ibm.mq GroupId. You can find both the com.ibm.mq.allclient.jar (typically used for standalone programs) and wmq.jmsra.rar (for use in Java EE application servers). The allclient.jar contains both the IBM MQ classes for JMS and the IBM MQ classes for Java.
Important: Using the Apache Maven Assembly Plugin jar-with-dependencies format to build an application which includes the IBM MQ relocatable JAR file is not supported.
In a pom.xml file processed by the maven command, you add dependencies for these JAR files as shown in the following examples:
To show the relationship between your application code and com.ibm.mq.allclient.jar:
<dependency>
        <groupId>com.ibm.mq</groupId>
        <artifactId>com.ibm.mq.allclient</artifactId>
        <version>9.2.2.0</version>
    </dependency>

For using the Java EE resource adapter:
<dependency>
     <groupId>com.ibm.mq</groupId>
     <artifactId>wmq.jmsra</artifactId>
     <version>9.2.2.0</version>
 </dependency>

For an example of a simple project in Eclipse to run a JMS project, see the IBM Developer article Developing Java applications for MQ just got easier with Maven.
