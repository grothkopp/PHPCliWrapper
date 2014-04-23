<?php

namespace CliWrapper\Pdo
{

  class PdoCliCommand extends \CliWrapper\CliCommand {
    public $con = null;
    public $tables = [];
    public $colums = [];

    function __construct($con){
      $this->con = $con;

      // get tables
      $result = $con->query("SHOW TABLES");
      while ($row = $result->fetch(\PDO::FETCH_NUM)) {
        $this->tables[] = $row[0];
      }

      // get colums
      foreach($this->tables as $table){
        $cols = array();
        $result = $con->query("DESCRIBE $table");
        while ($row = $result->fetch(\PDO::FETCH_NUM)) {
          $cols[] = $row[0];
        }
        $this->colums[$table] = $cols;
      }


    }

    function buildQuery($prefix,$path) {

      $q = $prefix;
      $q .= " FROM `".$path[0]."` ";

      $cond = $path;
      array_shift($cond);

      if(count($cond)>0) $q .= "WHERE ".implode(" AND ",$cond); 

      return $q;
    }


    function count($path = null){
      if(is_array($path) && count($path) >0){

        try {
          $count = $this->con->query($this->buildQuery("SELECT count(*) ",$path))->fetchColumn(); 
        }
        catch(\PDOException $e){
          echo $e->getMessage();
          echo "\n";
          $count = -1;
        }

        return $count;
      }

      return 0;

    }


  }
}
?>

