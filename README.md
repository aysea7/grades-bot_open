
# Grade viewer & editor (Telegram + Google Sheets)
![AGPLv3 License](https://img.shields.io/badge/License-GNU_AGPLv3-yellow.svg)
![date](https://img.shields.io/badge/Date-Autumn_2022-blue.svg)

This bot was created for me and my medical university classmates. It utilises the Telegram bot interface for getting access to the grades.

## Features

- Everything is done via text messages to a Telegram bot
- View/edit your marks in the pre-specified Google Spreadsheet
- View your marks from the university's online grade book
- Add books for different subjects into the shared directory on the server
- Download books from the shared directory
- Get a list of standard links for Zoom classes
## Background and Usage
In my university, we had to do online test assessments after each class. Then, we had to send our grades to the main student of the group, who would send a set of grades from all the group students to the corresponding professor. To make it easier, I had created a Google Spreadsheet with columns for the students' scores, the maximum score for each test, and the percent of success.

![image](https://github.com/aysea7/grades-bot_open/blob/main/readme_pics/google%20sheet.jpg?raw=true)

The structure of the text commands for the Google Sheets functionality is following:
```
/look [subject] [topic]
```
Colloquial subject names are listed in *lists.json*

![image](https://github.com/aysea7/grades-bot_open/blob/main/readme_pics/look_command.jpg?raw=true)

In order to see the offical grades on the university's online grade book website called EQX, the following command can be used:

```
/eqx [subject] [topic]
```
This bot sends the website's captcha in a cropped picture for the user to solve it and send the numerical answer in order for the bot to proceed.

Standard Zoom links can be retrieved using the */links* command:

![image](https://github.com/aysea7/grades-bot_open/blob/main/readme_pics/image.png?raw=true)

Books can be added to the shared server storage with this command:

```
/addbook [subject]
```
and  the can be retrieved like this:

```
/book [subject]
```
## Authors

- [Andrii Chubok](https://www.github.com/aysea7)

