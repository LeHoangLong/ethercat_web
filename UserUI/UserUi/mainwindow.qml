import QtQuick 2.4
import QtQuick.Controls 2.4
import QtQuick.Layouts 1.3
import "./"

ApplicationWindow {

    //title of the application
    title: qsTr("Hello World")
    width: 640
    height: 480
    visible: true
    objectName: "application_window"
    menuBar: TabBar{
        objectName: "menu bar"
        TabButton{
            text: qsTr("Machines")
            onClicked: {
                layout.currentIndex = 0
            }
        }

        TabButton{
            text: qsTr("Control")
            onClicked: {
                layout.currentIndex = 1
            }
        }
    }

    StackLayout {
        objectName: "layout"
        anchors.fill: parent
        currentIndex: 0
        MachinePage{
            objectName: "machine_page"
        }
        ControlPage {
            objectName: "control_page"
        }
    }

}
