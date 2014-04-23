<?php

namespace CliWrapper\Pdo
{

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
}
?>
