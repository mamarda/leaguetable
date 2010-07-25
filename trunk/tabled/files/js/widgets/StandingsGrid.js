( function() {

dojo.provide("leaguedata.widgets.StandingsGrid");

dojo.require("dijit.dijit");
dojo.require("dojo.data.ItemFileReadStore")
dojo.require("dojox.grid.DataGrid");

dojo.declare( "leaguedata.widgets.StandingsGrid", [dijit._Widget], {

   parentnode: null,

   gridcontainer: null,

   gridnode: null,

   grid: null,

   constructor: function( p, gridnode ){

      this.parentnode = gridnode;
   },
   
   reload: function(){
   		var newStore = new dojo.data.ItemFileReadStore({ url: "standings" } );
		this.grid.setStore(newStore);
   },

   postCreate: function(){
     
     this.gridcontainer = document.createElement( "div" ); 

     dojo.addClass( this.gridcontainer, "gridContainer" );

     this.parentnode.appendChild( this.gridcontainer );

     this.gridnode = document.createElement( "div" ); 

     dojo.addClass( this.gridnode, "standingsNode" );

     this.gridcontainer.appendChild( this.gridnode );

     this.gridnode.id = "standingsNode"; 

     var jsonStore = new dojo.data.ItemFileReadStore( { url: "standings" } );

     var layout= [ 	{ field: "team", width: "auto", name: "Team" },
    				{ field: "played", width: "30px", styles: 'text-align: center;', name: "P" },
     				{ field: "wins", width: "30px", styles: 'text-align: center;', name: "W" },
     				{ field: "draws", width: "30px", styles: 'text-align: center;', name: "D" },
    				{ field: "losses", width: "30px", styles: 'text-align: center;', name: "L" },
		   			{ field: "goalsfor", width: "30px", styles: 'text-align: center;', name: "GF" },
		   			{ field: "goalsagainst", width: "30px", styles: 'text-align: center;', name: "GA" },
		   			{ field: "difference", width: "30px", styles: 'text-align: center;', name: "GD" },
		   			{ field: "points", width: "50px", styles: 'text-align: center;', name: "Pts" } ];
 
     this.grid = new dojox.grid.DataGrid( { query: { standing: '*' },
				       store: jsonStore,
				       structure: layout,
				       rowsPerPage: 20,
				       sortInfo: -9,
				       sortOrder: 'ascending'
				       }, 'standingsNode' );

     this.grid.startup();
   }
   
});

})();
