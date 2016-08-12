import groovy.json.*
env.ViewClientBuildNum = ViewClientBuildNum
@NonCPS
def jsonParse(def json) {
   new groovy.json.JsonSlurperClassic().parseText(json)
}

stage '1. Parsing requirement'

node('viewci') {
   echo "Start view ci for build: ${env.ViewClientBuildNum}"
   git url:'https://github.com/zhanglin-zhou/testCI.git'
   sh "python parseRequirement.py requirement > requirements.json"
   stash name: "requirement", includes: "requirements.json"
}

stage '2. Requesting resource'
lock('viewci_resouce_pool') {
   node('viewci') {
      step([$class: 'WsCleanup'])
      git credentialsId:'d5e3ab3b-57eb-4698-ac9e-0537a275f28a', url:'https://github.com/zhanglin-zhou/testCI.git'
      unstash "requirement"
      sh "python requestResource.py -a requirements.json -p resources_pool.json > resources.json"
      sh "git add resources_pool.json"
      sh "git commit --file resources.json"
      withCredentials([[$class: 'UsernamePasswordMultiBinding', credentialsId: 'd5e3ab3b-57eb-4698-ac9e-0537a275f28a', usernameVariable: 'GIT_USERNAME', passwordVariable: 'GIT_PASSWORD']]) {
         String encoded_password = java.net.URLEncoder.encode(env.GIT_PASSWORD, "UTF-8")
         sh("git push https://${env.GIT_USERNAME}:${encoded_password}@github.com/zhanglin-zhou/testCI.git")
      }
      stash name: "resource", includes: "resources.json"
   }
}

node('viewci') {
   try {
      stage '3. Deploy and run test cases'
      git url:'https://github.com/zhanglin-zhou/testCI.git'
      unstash "resource"
      def resources = jsonParse(readFile("resources.json"))
      def runners = [:]
      for (int i = 0; i < resources.size(); i++) {
         def resource = resources[i];
         def label = resource["os"]
         echo "${resource}"
         runners[i] = {
            node(label) {
               echo "Running in label: ${label} for resource:"
               echo "${(new JsonBuilder(resource).toPrettyString())}"
               //git url:'https://github.com/zhanglin-zhou/testCI.git'
               writeFile file: "resource.json", text: (new JsonBuilder(resource).toString())
               //sh "python deployAndRun.py $ViewClientBuildNum resources.json > log"
            }
         }
      }
      parallel runners
   } catch(Exception ex) {
      println("Catching the exception")
      throw ex
   } finally {
      stage '4. Release resources'
      lock('viewci_resouce_pool') {
         node('viewci') {
            step([$class: 'WsCleanup'])
            git credentialsId:'d5e3ab3b-57eb-4698-ac9e-0537a275f28a', url:'https://github.com/zhanglin-zhou/testCI.git'
            unstash "resource"
            sh "python requestResource.py -r resources.json -p resources_pool.json"
            sh "git add resources_pool.json"
            sh "git commit --file resources.json"
            withCredentials([[$class: 'UsernamePasswordMultiBinding', credentialsId: 'd5e3ab3b-57eb-4698-ac9e-0537a275f28a', usernameVariable: 'GIT_USERNAME', passwordVariable: 'GIT_PASSWORD']]) {
               String encoded_password = java.net.URLEncoder.encode(env.GIT_PASSWORD, "UTF-8")
               sh("git push https://${env.GIT_USERNAME}:${encoded_password}@github.com/zhanglin-zhou/testCI.git")
            }   
         }
      }
   }
}

