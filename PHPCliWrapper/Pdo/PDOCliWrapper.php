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

class ListCommand extends PdoCliCommand {

  function command(&$path,$cmds){
    $results = $this->con->query($this->buildQuery("SELECT * ",$path));

    array_shift($cmds);
    if(count($path >0)){

    $keys = $cmds;
    if(count($keys) == 0) $keys = array_slice($this->colums[$path[0]],0,5); 

    $i=0;
    $items = [];

    while($r = $results->fetch(\PDO::FETCH_ASSOC)){

      $i++;
      reset($keys);
      $row = [];
      foreach($keys as $key) 
        if($key != "")
        {
          try {
            $val = $r[$key]; 
            if(is_array($val))
              $out = '["'.implode('","',$val).'"]'; 
            else if(is_numeric($val))
              $out = $val; 
            else
              $out = '"'.$val.'"';
            $row[$key] = $out;
          } catch (Exception $e) { echo "field does not exist";}

        }
       $items[] = $row;
    }

    \CliWrapper\CliHelper::prettyPrint($items,' ');
    
    }
  }

  function complete($path,$cmds){ 
 
    if(count($path) > 0){
     return $this->colums[$path[0]];
    }
  }

}

class ShowCommand extends PdoCliCommand {

function command(&$path,$cmds){

    $id="";
    if(count($cmds) == 3) {
      $class = $cmds[1];
      $id = $cmds[2];
    }

    if(count($cmds) == 2) {
      $id = $cmds[1];

      if(count($path)>0){$class = $path[0];}
      else return;
    }

    if(count($cmds) == 1) {

      if(count($path)>0){$class = $path[0];}
      else return;

    }


    $cols = $this->colums[$class];

    if($id != "")
      $res= $this->con->query("SELECT * FROM `$class` WHERE id = $id")->fetch(\PDO::FETCH_ASSOC);
    else 
     {
      $res= $this->con->query($this->buildQuery("SELECT * ",$path))->fetch(\PDO::FETCH_ASSOC);
     }
    

    if($res != "")
      $items = [];

    foreach ($cols as $key){
      $val = $res[$key];
      if(is_array($val))
        $val = "[".implode(',',$val)."]"; 

      $items[] = ['attribute'=>$key.': ','value'=>$val];
    }

   \CliWrapper\CliHelper::prettyPrint($items,'.',10,[STR_PAD_RIGHT,STR_PAD_LEFT]);

  }

}


class SetCommand extends PdoCliCommand {

function command(&$path,$cmds){

    if(count($path)>0) $class = $path[0];
    else {echo "no selection\n"; return;};
       
    $cols = $this->colums[$class];

    if(in_array($cmds[1],$cols)) $col = $cmds[1];
    else {echo "argument 1 should be a valid column\n"; return;};
   
    if(count($cmds) > 2) {
    
      array_shift($cmds);
      array_shift($cmds);
      $vals = implode(" ",$cmds);

    }
    else {echo "there should be something to change."; return;};

      $q = "UPDATE `$class` SET $col=$vals ";

      $cond = $path;
      array_shift($cond);
      
      if(count($cond)>0) $q .= "WHERE ".implode(" AND ",$cond); 


       echo "\n";
       echo $q;
       echo "\n";

       echo "Are you sure you want to ddo this?  Type 'yes' to continue: ";
       $handle = fopen ("php://stdin","r");
       $line = fgets($handle);
       if(trim($line) != 'yes'){
           echo "query aborted!\n";
       }
       else{ 
         $res= $this->con->query($q)->execute();
           echo "query executed!\n";
         }
       echo "\n";
  }

  function complete($path,$cmds){ 
 
    if(count($path) > 0 ){
     return $this->colums[$path[0]];
    }
  }


}

class CdCommand extends PdoCliCommand {
  function command(&$path,$cmds){  

   array_shift($cmds);
   $c = $cmds[0];
   $full = implode(' ',$cmds);
   switch($c){

    case ".":
    break;

    case "..":
      array_pop($path);
    break;

    case "/";
      $path = [];
    break;

    case (in_array($c,$this->tables) && count(explode('/',$full))<2):
      if(count($path) == 0) array_push($path,$c);
    break;
 
    default:
        $c = implode(' ',$cmds);
        $parts = explode('/',$c);

        $savedpath = $path;
  
        if(\CliWrapper\CliHelper::isInteger($c)) $c = "id=$c";
        if(count($parts)>1) {
          foreach($parts as $part) $path[] = trim($part);
        }
        else if(count($path) > 0) array_push($path, $c);
        else echo "Table '$c' not found\n";

        if($this->count($path) == -1) $path = $savedpath;
   }
 
    return $this->count($path);

  }

  function complete($path,$cmds){ 
 
    if(count($path) == 0){
     return $this->tables;
    }
    else {
     return $this->colums[$path[0]];
    }
  }


}
}

?>
