# Course Dashboard

A Shiny dashboard for students to choose courses and be able to share a URL with their advisor.

This template gives you a more "complete" dashboard for exploring the tips dataset. For an overview of what's here, visit [this article](https://shiny.posit.co/py/docs/user-interfaces.html).

## How to deploy:

- each time (you need to be in the main project folder, check in terminal with `pwd`)

```
rsconnect deploy shiny ./ --name ddi-talent --title course-dashboard-development
rsconnect deploy shiny ./ --name ddi-talent --title course-dashboard
``

- just once:

 install cli Command Line Interface
```

pip install rsconnect-python

or 

pip3 install rsconnect-python


```

authorise (this requires token - talk to Pawel to get it set up)

```

rsconnect add --account ddi-talent --name ddi-talent --token 08A88A6579E22FA92788487D15849722 --secret <SECRET>

```

Note: you might need


pip install Jinja2




```
