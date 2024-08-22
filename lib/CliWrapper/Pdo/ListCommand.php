<?php

namespace CliWrapper\Pdo
{

  class ListCommand extends PdoCliCommand {

    function command(&$path,$cmds){
      $results = $this->con->query($this->buildQuery("SELECT * ",$path));

      array_shift($cmds);
      if(count($path) > 0){

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
}
?>
