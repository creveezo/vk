Мой проект производит несложную аналитику сообщества Вконтакте. На главной странице пользователь вводит ID или короткое название интересующего его сообщества и получает в ответ анализ аудитории данного сообщества. Анализ отображается графически, в основном используются bar-charts и pie-charts.

Для извлечения данных я работала с VK API (далее с помощью pandas приводила данные в нужный мне вид), написала приложение на flask, оформила несколько html-страничек с помощью css и bootstrap. Для визуализации (графиков) я изначально планировала использовать matplotlib, но возникла проблема с хранением и отображением нарисованных графиков. Поэтому, чтобы графики рисовались сразу на стороне пользователя, для визуализации я использовала джаваскрипт библиотеку Chart.js

Ссылка на сайт: https://vkstat.olga.boba.ru/
