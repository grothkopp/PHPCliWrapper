<?php 

namespace CliWrapper {

  class CliHelper {
    public static function prettyPrint($values,$delim = ' ',$min = 0,$options = [],$legend_interval=50){

      $max = [];

      if(count($values)>0 && $legend_interval>0){
        $legend = [];
        foreach($values[0] as $key=>$val) $legend[$key] = $key; 

        $values2 = [];
        $i=0;
        foreach ($values as $row)
        {
          if(($i % $legend_interval) == 0) $values2[]=$legend;
          $values2[] = $row;
          $i++;
        }
      }
      else $values2=$values;

      $legend_interval++;

      foreach ($values2 as $row)
      {
        foreach ($row as $key => $val)
        {
          if(!array_key_exists($key,$max)) $max[$key] = $min;
          $l = strlen($val."" );
          if($max[$key] < $l && $l < 60) $max[$key] = $l;
        }
      }

      reset($values2);
      $i=0;
      foreach ($values2 as $row)
      {
        if(($i % $legend_interval) == 0) echo "\033[40m";
        foreach ($row as $key => $val)
        {

          $option =  (!($val == (string)(float)$val)) ? STR_PAD_RIGHT : STR_PAD_LEFT;
          $option =  (array_key_exists($key,$options)) ? $options[$key] : $option;

          echo str_pad($val,$max[$key],$delim,$option)." ";
        }
        if(($i % $legend_interval) == 0) echo "\033[0m";
        $i++;
        echo "\n";
      }

    }


    public static function isInteger($input){
      return(ctype_digit(strval($input)));
    }


  }

}
