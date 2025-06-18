# Awesome recipes
The application allows the user to add and managing cooking recipes. It allows the user to register, like other recipes and displaying them in a common way such as order by most recent, most popular, most liked. The recipes could be assigned to categories, cuisines each one has got detailed preparation instructions, allergens list.

## UX
The project is built in the minimal layout. Each recipe has got statistic such as views, likes, date created so the user could order its own way on the archive page. To add recipe a user need to register. The application has implemented simple ACL(access-control-list) protection, for example, the author can't edit/delete recipe someone else.

[The wireframe](https://xd.adobe.com/view/634d2933-4989-4354-4df1-ba55f3eb927e-157c/?fullscreen)

### Features
* Registration user can create own account to add own recipes, like the others and display them
* The website prevent votes for own recipe
* Users can't delete someone recipe or edit
* Users can vote for a recipe only once
* Views are counted only once when user enter the recipe view is incremented if refresh the page it isn't counted this is done by session to prevent the collection of fake data 
* Authentication by username and password
* Passwords are stored in the database as a hash created by 256-bit algorithm
* Orders recipes by: most popular, most liked, most recent
* Displaying user recipes, user liked recipes


### Features to implement
* Add lost password
* Search recipe by name

## Technologies used
* HTML5
* [MongoDB](https://www.mongodb.com/)
    * for storing app data
* [Flask](http://flask.pocoo.org/)
    * for building app backend and render the frontend (Jinja templates) 
* ES6 Support via [babel (v7)](https://babeljs.io/)
    * The project uses babel for compiling ES7 to ES5
* [Materialize](https://materializecss.com/)
    * Framework used for frontend development
* [JQuery](https://jquery.com/)
    * The project uses jquery for DOM manipulation and AJAX calls
* [SCSS](https://sass-lang.com/)
    * The project uses SCSS Preprocessors for compiling to CSS
* Python dotenv
    * The project used dotenv library to store secret data
* [Webpack](https://webpack.js.org/)
    * The project uses webpack for bundling the assets
* AdobeXD [wireframe](https://xd.adobe.com/view/634d2933-4989-4354-4df1-ba55f3eb927e-157c/?fullscreen)

## Testing
* Unit test is written to check the functionality of the routes on events logins, edit, delete 
* Form unit test is written to check forms validation
* The website has been tested on various screen sizes

## Deployment
The application is deployed to [Heroku](https://awesome-recipes-ci.herokuapp.com/)
The project used dotenv library to store secret data

### Assets source files
Assets files are in assets folder

### Compiled files
Compiled files are in the static folder

### Installation
`npm install`

### Start Dev Server
`npm start`

### Build production version
When you run npm run build we use the mini-css-extract-plugin to move the css to a separate file. The CSS file gets included in the head of the index.html.

`npm run build`


## Credits
* Recipes were scrapped from [Donal Skehan website](http://www.donalskehan.com/)
* Webpack [boilerplate](https://github.com/wbkd/webpack-starter)
* Images used from [Unsplash](https://unsplash.com/)
