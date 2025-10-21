#ifndef APP_HTTPD_H
#define APP_HTTPD_H

#include "esp_http_server.h"

extern httpd_handle_t stream_httpd;
extern httpd_handle_t camera_httpd;
extern int led_duty;
extern bool isStreaming;

void startCameraServer();
void setupLedFlash();
void enable_led(bool enable);

#endif // APP_HTTPD_H
