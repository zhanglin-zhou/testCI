import groovy.json.*
env.ViewClientBuildNum = ViewClientBuildNum
@NonCPS
def jsonParse(def json) {
   new groovy.json.JsonSlurperClassic().parseText(json)
}


node('viewci') {

   stage '1. Parsing requirement'

   echo "Start view ci for build: ${env.ViewClientBuildNum}"
   git credentialsId:'d5e3ab3b-57eb-4698-ac9e-0537a275f28a', url:'https://github.com/zhanglin-zhou/testCI.git'
   sh "python parseRequirement.py requirement > requirements.json"
   stash name: "requirement", includes: "requirements.json"

   stage '2. Requesting resource'

   lock('viewci_resouce_pool') {
      unstash "requirement"
      sh "python requestResource.py -a requirements.json -p resources_pool.json > resources.json"
      sh "git pull --no-edit origin master"
      sh "git add resources_pool.json"
      sh "git commit --file resources.json"
      withCredentials([[$class: 'UsernamePasswordMultiBinding', credentialsId: 'd5e3ab3b-57eb-4698-ac9e-0537a275f28a', usernameVariable: 'GIT_USERNAME', passwordVariable: 'GIT_PASSWORD']]) {
         String encoded_password = java.net.URLEncoder.encode(env.GIT_PASSWORD, "UTF-8")
         sh("git push https://${env.GIT_USERNAME}:${encoded_password}@github.com/zhanglin-zhou/testCI.git")
      }
      stash name: "resource", includes: "resources.json"
   }

   stage '3. Deploy and run test cases'

   try {
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
               git url:'https://github.com/zhanglin-zhou/testCI.git'
               writeFile file: "resource.json", text: (new JsonBuilder(resource).toString())
               sh "python deploy/deploy_viewclientmac.py -c -b '${env.ViewClientBuildNum }' -i"
               if (resource["was"] == "true") {
                  p4sync charset: 'none', credential: '9ec58a67-7f5a-4b9b-9c2d-a05921fe8669', depotPath: '//depot/non-framework/BFG/view-monaco/Linux', populate: [$class: 'AutoCleanImpl', delete: true, modtime: false, parallel: [enable: false, minbytes: '1024', minfiles: '1', path: '/usr/local/bin/p4', threads: '4'], pin: '', quiet: true, replace: true]
                  // run test case
               } else {
                  // run test case
               }
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
         unstash "resource"
         sh "python requestResource.py -r resources.json -p resources_pool.json"
         sh "git add resources_pool.json"
         sh "git pull --no-edit origin master"
         sh "git commit --file resources.json"
         withCredentials([[$class: 'UsernamePasswordMultiBinding', credentialsId: 'd5e3ab3b-57eb-4698-ac9e-0537a275f28a', usernameVariable: 'GIT_USERNAME', passwordVariable: 'GIT_PASSWORD']]) {
            String encoded_password = java.net.URLEncoder.encode(env.GIT_PASSWORD, "UTF-8")
            sh("git push https://${env.GIT_USERNAME}:${encoded_password}@github.com/zhanglin-zhou/testCI.git")
         }
      }
   }

   stage '5. Collect log'


}
