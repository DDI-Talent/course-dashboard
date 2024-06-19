# Course Dashboard

A Shiny dashboard for students to choose courses and be able to share a URL with their advisor.

This template gives you a more "complete" dashboard for exploring the tips dataset. For an overview of what's here, visit [this article](https://shiny.posit.co/py/docs/user-interfaces.html).

## How to deploy:

- each time (you need to be in the main project folder, check in terminal with `pwd`)

```
rsconnect deploy shiny ./ --name ddi-talent --title course-dashboard
``

- just once:

 install cli
```

pip install rsconnect-python`

```

authorise (this requires token - talk to Pawel to get it set up)

```

rsconnect add --account ddi-talent --name ddi-talent --token 234567898765432456789 --secret <SECRET>

```

Note: you might need


pip install Jinja2




```
