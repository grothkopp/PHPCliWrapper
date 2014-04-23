# PHPCLIWrapper: a small framework that helps you build commandline tools in PHP

# About 

With the included PDO commands you can use PHPCLIWrapper as a PDO commandline interface.
You can also write your own commands and use this library for whatever you like.

# Usage
1. You can load and run PHPCLiWrapper like this:
```$cli = new CliWrapper\Cli();
$cli->addCommand('list', new CliWrapper\Pdo\ListCommand($connection));
$cli->addCommand('show', new CliWrapper\Pdo\ShowCommand($connection));
$cli->addCommand('set',  new CliWrapper\Pdo\SetCommand($connection));
$cli->addCommand('cd',   new CliWrapper\Pdo\CdCommand($connection));

$cli->run();
```

2. Run your program

3. Use the builtin commands like "history" and the additional loaded commands

# Installing 

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


