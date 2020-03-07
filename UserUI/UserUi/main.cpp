#include "mainwindow.h"

#include <QApplication>
#include <QtQml/qqmlapplicationengine.h>
#include <QtQuick/QtQuick>
#include "loginhandler.h"

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    //MainWindow w;
    //w.show();

    LoginHandler handler;
    QQmlApplicationEngine engine;
    engine.load(QUrl(QStringLiteral("../UserUi/mainwindow.qml")));

    QObject *main_stack_layout = engine.rootObjects().first()->findChild<QObject*>("layout");

    if (main_stack_layout == nullptr){
        qDebug() << "cannot find main_stack_layout";
    }else{
        qDebug() << "found main_stack_layout";
    }

    QObject *machine_page = main_stack_layout->findChild<QObject*>("machine_page");

    if (machine_page == nullptr){
        qDebug() << "cannot find page";
    }else{
        qDebug() << "found page";
    }

    QObject *login_button = machine_page->findChild<QObject*>("login_button");
    if (login_button  == nullptr){
        qDebug() << "cannot find button";
    }else{
        qDebug() << "found button";
    }

    LoginHandler login_handler;
    engine.rootContext()->setContextProperty("login_handler_cpp", &login_handler);

    //QQuickView view(QUrl("qrc:/mainwindow.qml"));
    //QQuickView view(QUrl(QStringLiteral("../UserUi/mainwindow.qml")));
    //view.show();
    return a.exec();
}
