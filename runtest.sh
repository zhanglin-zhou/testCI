export PATH=$PATH:~/jython2.7.0/bin/
export CLASSPATH=/Applications/Sikuli-IDE.app/Contents/Resources/Java/sikuli-script.jar:~/mm-mysql-2.0.7.jar
export TESTOS=mac
export JAVA_TOOL_OPTIONS='-Djava.awt.headless=false'
launchctl setenv VMWARE_VIEW_DEBUG_LOGGING "1"
launchctl setenv VMWARE_VIEW_USBD_LOG_OPTIONS "-o log:trace"
chmod +w ./conf/automation.ini
chmod +w ./conf/database.ini
cp ./automation.ini.test ./conf/automation.ini
cd ./lib
jython executetests.py -n $1 -s mac_bat -i test2
