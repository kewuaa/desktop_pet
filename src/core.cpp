#include <iostream>
#include <random>
#ifndef _DEBUG
#include <windows.h>
#endif

#include "QtCore/QPoint"
#include "QtCore/QSize"
#include "QtCore/QTimer"
#include "QtGui/QGuiApplication"
#include "QtGui/QScreen"
#include "QtGui/QIcon"
#include "QtGui/QMouseEvent"
#include "QtWidgets/QApplication"
#include "QtWidgets/QAction"
#include "QtWidgets/QLabel"
#include "QtWidgets/QWidget"
#include "QtWidgets/QVBoxLayout"
#include "QtWidgets/QMenu"
#include "QtWidgets/QSystemTrayIcon"

#include "image.hpp"

class Pet: QWidget {
    QTimer _timer;
    bool _follow_mouse;
    QPoint _mouse_press_pos;
    int _pos[2];
    QLabel _img_label;

    void _init_ui() {
        using namespace Qt;
        QScreen* screen = QGuiApplication::primaryScreen();
        QSize screen_size = screen->size();
        _pos[0] = screen_size.width() - width();
        _pos[1] = screen_size.height() - height();
        setWindowFlags(WindowType::SubWindow | WindowType::FramelessWindowHint | WindowType::WindowStaysOnTopHint);
        setAutoFillBackground(false);
        setAttribute(WidgetAttribute::WA_TranslucentBackground, true);
        repaint();
        QVBoxLayout* vbox = new QVBoxLayout;
        setLayout(vbox);
        vbox->addWidget(&_img_label);
        _set_system_menu();
        show();
    }

    void _set_system_menu() {
        const QIcon icon = std::move(PetImage::get_icon());
        QAction* quit_action = new QAction("退出", this);
        quit_action->setIcon(icon);
        QMenu* sys_menu = new QMenu(this);
        sys_menu->addAction(quit_action);
        QSystemTrayIcon* tray_icon = new QSystemTrayIcon(this);
        tray_icon->setContextMenu(sys_menu);
        tray_icon->setIcon(icon);
        tray_icon->show();
        connect(
            quit_action,
            &QAction::triggered,
            this,
            [this]() {
                this->_timer.stop();
                this->close();
                exit(0);
            }
        );
    }

    void show() {
        std::random_device seed;
        std::default_random_engine engine(seed());
        std::uniform_real_distribution<> distrib(0, 1);
        move(
            (int)(_pos[0] * distrib(engine)),
            (int)(_pos[1] * distrib(engine))
        );
        QWidget::show();
    }

    void mousePressEvent(QMouseEvent* event) {
        if (event->button() == Qt::MouseButton::LeftButton) {
            _follow_mouse = true;
            _mouse_press_pos = pos() - event->globalPos();
            setCursor(QCursor(Qt::CursorShape::OpenHandCursor));
        }
        QWidget::mousePressEvent(event);
    }

    void mouseMoveEvent(QMouseEvent* event) {
        if (_follow_mouse) {
            move(event->globalPos() + _mouse_press_pos);
        }
        QWidget::mouseMoveEvent(event);
    }

    void mouseReleaseEvent(QMouseEvent* event) {
        if (event->button() == Qt::MouseButton::LeftButton) {
            if (_follow_mouse) {
                _follow_mouse = false;
                setCursor(QCursor(Qt::CursorShape::ArrowCursor));
            }
        }
        QWidget::mouseReleaseEvent(event);
    }

    public:
    Pet(): _timer(this), _follow_mouse(false), _mouse_press_pos(0, 0), _pos{0, 0}, _img_label(this) {
        PetImage::load();
        _timer.setInterval(500);
        connect(
            &_timer,
            &QTimer::timeout,
            this,
            [this]() {
                PetImage::set(this->_img_label);
            }
        );
        _timer.start();
        _init_ui();
    };
};


int main(int argc, char** argv) {
#ifndef _DEBUG
    const auto hwnd = FindWindowA("ConsoleWindowClass", NULL);
    if (hwnd) {
        ShowWindow(hwnd, SW_HIDE);
    }
#endif
    QApplication app(argc, argv);
    Pet pet;
    app.exec();
    return 0;
}
