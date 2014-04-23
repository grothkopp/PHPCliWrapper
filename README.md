# PHPCLIWrapper
## About
PHPCLIWrapper is a small framework that helps you build commandline tools in PHP.<br>
With the included PDO commands you can use PHPCLIWrapper as a PDO commandline interface.<br>
You can also write your own commands and use this library for whatever purpose you like.

## Demo
<img src="screencast.gif">

## Usage
1. You can load and run PHPCLiWrapper like this:
```
$cli = new CliWrapper\Cli();

$cli->addCommand('list', new CliWrapper\Pdo\ListCommand($connection));
$cli->addCommand('show', new CliWrapper\Pdo\ShowCommand($connection));
$cli->addCommand('set',  new CliWrapper\Pdo\SetCommand($connection));
$cli->addCommand('cd',   new CliWrapper\Pdo\CdCommand($connection));

$cli->run();
```

## Installing 

You can install PHPCLIWrapper with Composer.
Add these lines to your composer.json

```
 "require": {
     "grothkopp/PHPCliWrapper": "0.1.*"
   },
  "repositories": [
   {
      "type": "vcs",
      "url": "git@github.com:grothkopp/phpcliwrapper.git"
    }

```

## License
PHPCLIWrapper
Copyright (c) 2014, Stefan Grothkopp, All rights reserved.

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 3.0 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library.


