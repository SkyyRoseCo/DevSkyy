/* Offline directing proposals. Figure colors identify blocking roles, not garment fidelity. */
window.BOARD_DATA = (() => {
  const person = (id, x, pose = 'rest', extra = {}) => ({id, x, y: 755, pose, scale: 1, ...extra});
  const cast = (r, s, p = person('purple', 470, 'rest', {scale:.78,y:680})) => [r,s,p];
  const shot = (seconds, name, action, why, figures, extra = {}) => ({seconds,name,action,why,figures,camera:[0,0,540,960],...extra});
  return {
    version:'R2', canvas:'9:16', kind:'SCHEMATIC_TIMED_BOARDS_NOT_GENERATED_FOOTAGE',
    routes:[
      {id:'A',title:'She Moved First',mechanism:'Imitation becomes initiative',question:'Who is setting the rhythm?',risk:'The leadership reversal must read as a decision, not a repeating pose loop.',shots:[
        shot(3,'A presence at the edge','Red model settles frontally; only part of a second figure is visible. Purple is planted in the depth.','Establish product and an unexplained second presence.',cast(person('red',185),person('skyy',415)),{camera:[80,190,315,560],fronts:['kids-001']}),
        shot(3,'Skyy is revealed','The frame widens: Skyy shares the red model’s stance. They notice each other.','Reveal the recurring character clearly.',cast(person('red',170,'rest',{gaze:1}),person('skyy',355,'rest',{gaze:-1})),{fronts:['kids-001'],cut:true}),
        shot(3,'The test','Red deliberately places a hand on the hip. Skyy watches and waits one beat.','Make imitation a visible question.',cast(person('red',170,'leftHip',{gaze:1}),person('skyy',355,'rest',{gaze:-1})),{fronts:['kids-001']}),
        shot(3,'The answer','Skyy repeats the hand-on-hip stance; red watches.','Confirm the rule before reversing it.',cast(person('red',170,'leftHip',{gaze:1}),person('skyy',355,'leftHip',{gaze:-1})),{fronts:['kids-001']}),
        shot(3,'Her own move','Red holds and watches. Skyy lowers that hand, shifts to the other hip and steps sideways.','Skyy initiates rather than copies.',cast(person('red',170,'leftHip',{gaze:1}),person('skyy',330,'rightHip',{gaze:-1})),{fronts:['kids-001']}),
        shot(3,'The lead changes','Red lowers the original hand and mirrors Skyy’s new stance. Skyy watches the response.','The child now responds to Skyy.',cast(person('red',195,'rightHip',{gaze:1}),person('skyy',330,'rightHip',{gaze:-1})),{fronts:['kids-001']}),
        shot(3,'A third move','The planted purple model steps forward and places both hands on the hips. The pair watch this new move.','Give the second child a reason to join and an action of their own.',cast(person('red',120,'rightHip',{gaze:1}),person('skyy',265,'rightHip',{gaze:1}),person('purple',410,'bothHip',{gaze:-1})),{fronts:['kids-001','kids-002'],cut:true}),
        shot(3,'Everyone leads','Red and Skyy respond with the same two-handed stance. Settle all three frontally.','The exchange now belongs to all three; hold both products.',cast(person('red',120,'bothHip'),person('skyy',265,'bothHip'),person('purple',410,'bothHip')),{fronts:['kids-001','kids-002']})
      ]},
      {id:'B',title:'Out of the Frame',mechanism:'A solo portrait becomes a choice to join',question:'Will the child keep the privileged position or join the others?',risk:'Leaving the central seat may read as arbitrary unless the separation is legible.',shots:[
        shot(3,'The solo portrait','Red occupies the central throne-derived seat; another child is visible at the edge.','Establish the prized solo composition.',cast(person('red',270,'seated',{y:660}),person('skyy',470,'rest',{hidden:true}),person('purple',470,'rest',{scale:.75,y:715})),{seat:true,camera:[85,90,370,658],fronts:['kids-001']}),
        shot(3,'The interruption','Skyy crosses into the edge of the portrait while red holds the pose.','Interrupt the perfect isolated image.',cast(person('red',270,'seated',{y:660}),person('skyy',125),person('purple',470,'rest',{scale:.75,y:715})),{seat:true,cut:true}),
        shot(3,'Restore the pose','Red resets a formal pose. Skyy pauses, then moves toward the purple model.','Show two possible compositions.',cast(person('red',270,'seated',{y:660}),person('skyy',380),person('purple',470)),{seat:true,fronts:['kids-001']}),
        shot(3,'The other picture','Skyy and purple stand together beside the seat. Red turns toward them.','Make company visibly preferable to isolation.',cast(person('red',270,'seated',{y:660}),person('skyy',380,'leftHip'),person('purple',465,'rightHip')),{seat:true}),
        shot(3,'Leave the center','Red stands and steps away from the privileged seat.','A physical choice changes the image.',cast(person('red',220),person('skyy',380),person('purple',465)),{seat:true}),
        shot(3,'Choose the group','Skyy and purple move inward as red joins; the seat stays empty.','Make the abandoned alternative visible.',cast(person('red',140),person('skyy',280),person('purple',420)),{seat:true}),
        shot(4,'The new portrait','All three hold the shared foreground. The empty seat remains behind.','Complete the visual contrast and show both products.',cast(person('red',140),person('skyy',280),person('purple',420)),{seat:true,fronts:['kids-001','kids-002']})
      ]},
      {id:'C',title:'Room for the View',mechanism:'Competing positions become a shared solution',question:'How can both see through a changing obstruction?',risk:'Without moving scenery, the objective is hard to understand. This is a train-space test, not final production design.',shots:[
        shot(3,'The passing view','Red at the left window; purple in depth. Passing structure intermittently obscures the view.','Plant train movement and the desired view.',cast(person('red',135,'lookLeft'),person('skyy',470,'rest',{hidden:true})),{piers:true}),
        shot(3,'Another observer','Skyy appears at the right window trying to see the same view.','Reveal her through a shared objective.',cast(person('red',135,'lookLeft'),person('skyy',405,'lookRight')),{piers:true,cut:true}),
        shot(3,'The blocked positions','Red steps inward as a pier passes left; Skyy also steps inward from the right.','Bring both attempts into the same limited space.',cast(person('red',230,'lookLeft'),person('skyy',310,'lookRight')),{piers:true}),
        shot(3,'The pause','Both stop, recognizing they are blocking each other.','The old tactic does not work.',cast(person('red',230),person('skyy',310)),{piers:true}),
        shot(3,'Make room','Skyy steps back into the broad observation bay; red stays for one beat.','Offer a different spatial solution through action.',cast(person('red',230),person('skyy',350,'rest',{y:815})),{piers:true}),
        shot(3,'Share the position','Red steps back too; purple joins the available space.','Resolve the competing positions.',cast(person('red',125),person('skyy',270),person('purple',415)),{piers:false}),
        shot(4,'Together in the light','The obstruction clears behind them; cut to their fronts with the window beyond.','Resolve the view and provide product-readable coverage.',cast(person('red',125),person('skyy',270),person('purple',415)),{piers:false,fronts:['kids-001','kids-002'],cut:true})
      ]}
    ]
  };
})();
