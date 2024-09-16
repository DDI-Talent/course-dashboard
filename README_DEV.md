# Course Dashboard

A Shiny dashboard for students to choose courses and be able to share a URL with their advisor.

## Current deployed version

[Most recent deployed version https://ddi-talent.shinyapps.io/course-dashboard/](https://ddi-talent.shinyapps.io/course-dashboard/)


## Before first run

pip install -r requirements.txt


## How to deploy:

- each time (you need to be in the main project folder, check in terminal with `pwd`)

```
From Main Branch:

rsconnect deploy shiny ./ --name ddi-talent -a 12235352 --title course-dashboard  

From Dev branch:

rsconnect deploy shiny ./ --name ddi-talent -a 12215502 --title course-dashboard-development  

```


- just once:

install cli Command Line Interface
```

pip install rsconnect-python

```

or 
```

pip3 install rsconnect-python

```

authorise (this requires token - talk to Pawel to get it set up). Note for pawel, in https://www.shinyapps.io/admin/#/tokens

```

rsconnect add --account ddi-talent --name ddi-talent --token 234567898765432456789 --secret <SECRET>

```

Note: you might need


pip install Jinja2
pop install faicons

or

pip install -r requirements.txt 

```
