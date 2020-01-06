import QtQuick 2.3
import QtQuick.Controls 2.3
import QtQuick.Layouts 1.3
import QtQuick.Controls.Styles 1.4

Item {

    //Content Area
    ListModel{
        id: machineListModel
        ListElement{
            name: "local"
            last_login_time: "01/01/2001 01:01:01"
            selected: true
        }
        ListElement{
            name: "remote"
            last_login_time: "01/01/2001 01:01:01"
            selected: false
        }
    }

    Component {
        id: machineListDelegate
        //a button in the middle of the content area

        Row{
            width: childrenRect.width
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
        width: parent.width
        height: parent.height
        anchors.top: parent.top
        anchors.topMargin: 20
        anchors.left: parent.left
        anchors.leftMargin: 50
        spacing: 30
    }

    Button {
        id: login_button
        objectName: "login_button"
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 20
        anchors.rightMargin: 20
        height: 80
        width: 200
        signal loginButtonClicked()
        background: Rectangle {
            radius: myRoundButton.radius
            color: "blue"
        }

        //onPressed: {
        //    login_button.background.color = 'grey'
        //    login_button.loginButtonClicked()
        //}

        onPressed: login_button.loginButtonClicked()

        onReleased: {
            login_button.background.color = 'blue'
        }

        text: qsTr("Login")
        onLoginButtonClicked: login_handler_cpp.loginClicked()
    }
}
