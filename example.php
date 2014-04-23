<?php

require_once('PHPCLiWrapper.php');
require_once('PDO/PDOCLiWrapper.php');

$user = "";
$pass= "";
$host = "localhost";
$db = "db";

try {
  $connection = new PDO('mysql:host=i$host;dbname=$db', $user, $pass);


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
