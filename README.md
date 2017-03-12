##Stargate 
[![Build Status](https://travis-ci.org/sohaibfarooqi/stargate.svg?branch=master)](https://travis-ci.org/sohaibfarooqi/stargate)

Stargate let you expost JSON RESTFul APIs against Model resources. This project is under
development. Currently `GET` method has test cases written. Remaining view functions are yet to be 
tested. Docs for this project will be published soon on github pages.

This code is largely inspired from [Flask-Restless](https://github.com/jfinkels/flask-restless). It is 
indeed a great example for someone who wants to learn and understand how RESTFul APIs should be coded.

For quickstart please check [example app](../master/app/quickstart.py). 
For Documentation check out [Docs](https://sohaibfarooqi.github.io/stargate/).

###Features

Currently it supports following features:
 
 - Expose a restful interface against a resource
 - Customize endpoint
 	- Modify url prefix.
 	- Specify view decorators.
 	- Specify resource fields for response.
 	- Exclude some fields form response.
 	- Specify a different primary key for resource. Default is `id`.
 	- HTTP methods to be allowed on a resource
 - Collection filteration
 	- Filters
 	- Sorting
 	- Grouping
 	- Pagination
 - Partial Response.
 - Resource Expansion.
 - Resource attribute and relationship updation.
 - Resource Deletion.

###To-Do List

Stargate will provide following feature in future
 
 - Authentication/Authorization.
 - Rate limiting.
 - Schema Views.
 - Field validations.

###Final Notes

Feel free to contribute to this project. Suggest me changes for the betterment of this project. I will keep adding new features to this project.

Thanks.!	
