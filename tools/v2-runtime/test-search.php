<?php
$source=file_get_contents(__DIR__.'/../../wordpress-theme/skyyrose-flagship-2/functions.php');
$start=strpos($source,'/** Bound native public search');
if($start===false)throw new Exception('Missing bounded grouping');
function add_action(){}
function is_admin(){return false;}
function skyyrose2_collections(){return ['black-rose'=>[],'love-hurts'=>[],'signature'=>[],'kids-capsule'=>[]];}
eval(substr($source,$start));
foreach([['product','black-rose','products'],['post','black-rose','stories'],['page','black-rose','collections'],['page','faq','pages'],['attachment','black-rose','']] as [$type,$slug,$expected]){
 if(skyyrose2_search_result_group($type,$slug)!==$expected)throw new Exception('Nonexclusive grouping');
}
class SearchQuery {
 public array $vars=[];
 public function __construct(public bool $main,public bool $search){}
 public function is_main_query(){return $this->main;}
 public function is_search(){return $this->search;}
 public function get($key){return $this->vars[$key]??'';}
 public function set($key,$value){$this->vars[$key]=$value;}
}
$q=new SearchQuery(true,true);skyyrose2_bound_search_query($q);if($q->get('posts_per_page')!==24)throw new Exception('Unbounded search');
$q=new SearchQuery(false,true);skyyrose2_bound_search_query($q);if($q->vars)throw new Exception('Secondary query changed');
$q=new SearchQuery(true,false);skyyrose2_bound_search_query($q);if($q->vars)throw new Exception('Nonsearch query changed');
echo "PASS exclusive groups and native search boundary\n";
