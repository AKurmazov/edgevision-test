# EdgeVision Test Assignment
This project is a test assignment give by *EdgeVision*

### Running locally
The project uses Docker, so initially you have to build and run images using **docker-compose**
```
$ docker-compose up --build
```
This will create only one **sensor**. You can specify the number of sensors using `--scale <service>=<number>` parameter. For example, if the desired number of sensors is 8, the following command should be run:
```
$ docker-compose up --build --scale sensor=8
```
### Checking logs
Both **controller** and **manipulator** perfrom logging during its execution, the logs can be found here:
* controller/controller.log
* manipulator/manipulator.log