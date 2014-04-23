<?php 

namespace CliWrapper {

  class Cli {

    private $marksfile = ".cli_marks"; // file to store bookmarks
    private $prompting = true; // do we accept user input
    private $path      = [];   // virtual path describing the query
    private $history   = [];   // command history
    private $marks     = [];   // bookmarks
    private $commands  = ["cd","exit","history","mark","unmark","go"];
    private $cmdobj    = [];   // Command Objects 
    private $status = 0;       // command status

    function __construct(){
      $this->marks = unserialize(file_get_contents($this->marksfile));
    }


    function __destruct(){
    }

    function addCommand($name,$obj){
      $this->commands[]= $name;
      $this->cmdobj[$name] = $obj;
    }

    function run() {

      $this->install_handler();
      readline_completion_function(array($this,'callback_complete'));

      while ($this->prompting) {
        $w = NULL; $e = NULL; $r = array(STDIN);
        $n = stream_select($r, $w, $e, null);
        if ($n && in_array(STDIN, $r)) {
          // read a character, will call the callback when a newline is entered
          readline_callback_read_char();
        }
      }

      echo "Exit.\n";
    }

    function install_handler(){
      // build prompt
      $path = implode($this->path,"\033[37m / \033[0m");
      $c = $this->status;
      if($c == 1) { $color1 = "\033[32m"; $sep = "#"; }
      else        { $color1 = "\033[33m"; $sep = ">"; }
      if($c ==0) 
        if(count($this->path)>0)
          $color1 = "\033[31m";
        else
          $color1 = "\033[37m";

      readline_callback_handler_install("$color1"."[$c]\033[0m $path \033[037m$sep\033[0m ", array($this,'rl_callback'));
    }

    function rl_callback($ret)
    {

      if($ret != "") {
        $this->command($ret);
        readline_add_history($ret);
        array_push($this->history,$ret);
      }

      if ($ret == "exit") {
        $this->prompting = false;
        readline_callback_handler_remove();
      } else {
        $this->install_handler();
      }
    }

    function callback_complete($input, $index) {

      $buffer= "";
      $buffer = substr(readline_info()["line_buffer"],0,readline_info()['end']);
      $cmds = explode(" ",$buffer);
      $c = $cmds[0];

      $cmp1 = [];
      if(count($cmds) <= 1)
        $cmp1 = $this->commands;


      if (!in_array($c,$this->commands)){
        $c = "cd";
        $cmds = array_merge([$c],$cmds);
      }

      if(array_key_exists($c,$this->cmdobj))
        $cmp = $this->cmdobj[$c]->complete($this->path,$cmds);
      else
        $cmp = $this->{"complete_".$c}($cmds);

      if(!is_array($cmp)) $cmp = [];
      
      if(count($cmp) == 0) $cmp1 = $this->commands;

      $cmp = array_merge($cmp1,$cmp);

      sort($cmp);
      return $cmp;
    }


    function command($c){

      $cmds = explode(" ",$c);
      $c = $cmds[0];

      if (!in_array($c,$this->commands)){
        $c = "cd";
        $cmds = array_merge([$c],$cmds);
      }

      if(array_key_exists($c,$this->cmdobj))
        $status = $this->cmdobj[$c]->command($this->path,$cmds);
      else
        $status = $this->{"cmd_".$c}($cmds);

      if($status !== null) $this->status = $status;
    }

    function cmd_history() {
      echo implode("\n",$this->history)."\n";
    }
    function complete_history($cmd){ return []; }

    function cmd_exit() {}
    function complete_exit($cmd){ return []; }

    function cmd_mark($cmds){
      if(count($cmds)>1){
        $name = $cmds[1];
        $this->marks[$name]=['path'=>$this->path];
        file_put_contents($this->marksfile,serialize($this->marks));
      }
      else{
        $marks = [];

        foreach($this->marks as $name=>$mark){
          $marks[] = ['name' => $name.":",
            'path' => implode(" / ",$mark['path'])];
        }
        CliHelper::prettyPrint($marks,' ');
      }
    }

    function complete_mark($cmd){
      return $this->complete_go($cmd);
    }


    function cmd_unmark($cmds){
      if(count($cmds)>1){
        $name = $cmds[1];
        unset($this->marks[$name]);
        file_put_contents($this->marksfile,serialize($this->marks));
      }
    }

    function complete_unmark($cmd){
      return $this->complete_go($cmd);
    }

    function cmd_go($cmds){
      if(count($cmds)>1){
        $name = $cmds[1];
        if(array_key_exists($name,$this->marks)){
          $this->path = $this->marks[$name]["path"];
          $this->command('cd .');
        }
        else echo "mark not set\n";
      }
    }

    function complete_go($cmd){

      if(count($this->marks)>0){
        $cmp = [];

        foreach($this->marks as $key=>$mark){
          array_push($cmp,$key);
        }    
        return $cmp;
      }  

      return [];
    }

    function cmd_cd($cmds){  

      array_shift($cmds);
      $c = $cmds[0];
      $full = implode(' ',$cmds);
      switch($c){

        case "..":
          array_pop($this->path);
          break;

        case "/";
          $this->path = [];
          break;

        default:
          $c = implode(' ',$cmds);
          $parts = explode('/',$c);

          if(count($parts)>1) {
            foreach($parts as $part) $this->path[] = trim($part);
          }
          else array_push($this->path, $c);
      }

    }

    function complete_cd($cmds){ 
      return [];
    }

  }
}
