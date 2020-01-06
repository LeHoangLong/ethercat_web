import QtQuick 2.4
import QtQuick.Controls 2.4
import QtQuick.Layouts 1.3

Item {
    //Content Area
    ListModel{
        id: machineListModel
        ListElement{
            name: "abc"
            last_login_time: "01/01/2001 01:01:01"
            selected: true
        }
        ListElement{
            name: "def"
            last_login_time: "01/01/2001 01:01:01"
            selected: false
        }
    }

    Component {
        id: machineListDelegate
        //a button in the middle of the content area

        Row{
            anchors.topMargin: 100
            width: parent.width
            height: childrenRect.height

            Column{
                Text{
                    text: qsTr("machine name: " + name)
                }
                Text{
                    text: qsTr("last online: " + last_login_time)
                }
            }


            RadioButton {
                id: radio
                anchors.right: parent.right
                anchors.horizontalCenter: parent.horizontalCenter
                checked: selected
                onClicked: {
                    for (var i = 0; i < machineListModel.count; i++){
                        machineListModel.get(i).selected = false
                    }

                    selected = true
                }
            }
        }
    }


    ListView{
        model: machineListModel
        delegate: machineListDelegate
        width: 500
        height: parent.height
        anchors.top: menuBar.bottom
        anchors.topMargin: 50
        anchors.bottomMargin: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: 30
    }
}
