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
      git url:'https://github.com/zhanglin-zhou/testCI.git'
      unstash "requirement"
      sh "python requestResource.py -a requirements.json -p resources_pool.json > resources.json"
      sh "git add resources_pool.json"
      sh "git commit --file resources.json"
      sh "git push --set-upstream origin master"
      stash name: "resource", includes: "resources.json"
   }
}

stage '3. Deploy and run test cases'
node('viewci') {
   git credentialsId:'d5e3ab3b-57eb-4698-ac9e-0537a275f28a', url:'https://github.com/zhanglin-zhou/testCI.git'
   unstash "resource"
   def resources = jsonParse(readFile("resources.json"))
   def runners = [:]
   for (int i = 0; i < resources.size(); i++) {
      def resource = resources[i];
      def label = resource["os"]
      runners[i] = {
         node(label) {
            echo "Running in label: ${label}"
            //git url:'https://github.com/zhanglin-zhou/testCI.git'
            echo "${JsonOutput.toJson(resources[i])}"
            writeFile file: "resources.json", text: JsonOutput.toJson(resources[i])
            //sh "python deployAndRun.py $ViewClientBuildNum resources.json > log"
         }
      }
   }
   parallel runners
}

stage '4. Release resources'
lock('viewci_resouce_pool') {
   node('viewci') {
      step([$class: 'WsCleanup'])
      git credentialsId:'d5e3ab3b-57eb-4698-ac9e-0537a275f28a', url:'https://github.com/zhanglin-zhou/testCI.git'
      unstash "resource"
      sh "python requestResource.py -r resources.json -p resources_pool.json"
      sh "git add resources_pool.json"
      sh "git commit --file resources.json"
      sh "git push --set-upstream origin master"
   }
}
