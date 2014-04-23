<?php

// example CLIWrapper with PDO Modules

require_once('lib/CliWrapper/Cli.php');
require_once('lib/CliWrapper/CliCommand.php');
require_once('lib/CliWrapper/CliHelper.php');

require_once('lib/CliWrapper/Pdo/PdoCliCommand.php');
require_once('lib/CliWrapper/Pdo/ListCommand.php');
require_once('lib/CliWrapper/Pdo/ShowCommand.php');
require_once('lib/CliWrapper/Pdo/SetCommand.php');
require_once('lib/CliWrapper/Pdo/CdCommand.php');
// Configuration 

$user = "";
$pass= "";
$host = "localhost";
$db = "db";

// --------------

try {
  $connection = new PDO('mysql:host=i$host;dbname=$db', $user, $pass);

  // the CLIWrapper 
  $cli = new CliWrapper\Cli();
  $cli->addCommand('list', new CliWrapper\Pdo\ListCommand($connection));
  $cli->addCommand('show', new CliWrapper\Pdo\ShowCommand($connection));
  $cli->addCommand('set',  new CliWrapper\Pdo\SetCommand($connection));
  $cli->addCommand('cd',   new CliWrapper\Pdo\CdCommand($connection));

  $cli->run();

} catch (PDOException $e) {
  print "Error!: " . $e->getMessage() . "<br/>";
  die();
}


?>
