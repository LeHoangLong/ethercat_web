#ifndef LOGINHANDLER_H
#define LOGINHANDLER_H

#include <QObject>
#include <QRunnable>
#include <QThread>
#include <QDebug>

class LoginHandler : public QObject
{
Q_OBJECT
public slots:
    void loginClicked() {
       qDebug() << "Called the C++ slot with item";
    }
public:
    LoginHandler();
};

#endif // LOGINHANDLER_H
