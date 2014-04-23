<?php

namespace CliWrapper\Pdo
{

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
