# Jarvis lab assistant: Alexa/Amazon Echo Skill

_The lab partner that does things right!_

## Introduction
Jarvis is your personal assistant in the lab. He will tell you the steps to an experiment and store data for you. All you have to do is tell him too! Jarvis is built using Python 2.7 and AWS Lambda.

## How it Works
Jarvis knows what you want him to do by assigning certain key phrases and sentences to intents which Alexa passes to our program
for further processing and then builds a response to pass back to the Echo and then on too you. All the data that you input into
Jarvis is stored in the ERMrest relational database: (https://github.com/informatics-isi-edu/ermrest)

## How to Install
Clone Jarvis to your machine, then run the create deployment script. That should create a zip file which you can upload to 
AWS Lambda. Create an AWS Lambda project and link it to the AlexaSkillsKit. Enable this skill for your account and your free to
use Jarvis as you please.
