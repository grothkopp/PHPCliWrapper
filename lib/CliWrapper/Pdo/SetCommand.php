<?php

namespace CliWrapper\Pdo
{


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
}
?>
