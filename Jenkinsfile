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
   sh "python parseRequirement.py requirement > requirement.json"
   stash name: "requirement", includes: "requirements.json"
}

stage '2. Requesting resource'
node('viewci_pool_manager') {
   git url:'https://github.com/zhanglin-zhou/testCI.git'
   unstash "requirement"
   sh "python requestResource.py requirements.json resources.json"
   stash name: "resource", includes: "resources.json"
}

stage '3. Deploy and run test cases'
node('viewci') {
   git url:'https://github.com/zhanglin-zhou/testCI.git'
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
