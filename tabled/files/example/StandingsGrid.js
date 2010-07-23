( function() {

dojo.provide("ajax.example.StandingsGrid");

dojo.require("dijit.form.Button");

dojo.declare( "ajax.example.StandingsGrid", [dijit._Widget], {

   parentnode: null,

   gridcontainer: null,

   gridnode: null,

   grid: null,

   constructor: function( p, gridnode ){

      this.parentnode = gridnode;
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
     				{ field: "wins", width: "30px", styles: 'text-align: center;', name: "W" },
     				{ field: "draws", width: "30px", styles: 'text-align: center;', name: "D" },
    				{ field: "losses", width: "30px", styles: 'text-align: center;', name: "L" },
		   			{ field: "goalsfor", width: "30px", styles: 'text-align: center;', name: "GF" },
		   			{ field: "goalsagainst", width: "30px", styles: 'text-align: center;', name: "GA" },
		   			{ field: "difference", width: "30px", styles: 'text-align: center;', name: "D" },
		   			{ field: "points", width: "40px", styles: 'text-align: center;', name: "P" } ];
 
     this.grid = new dojox.grid.DataGrid( { query: { standing: '*' },
				       store: jsonStore,
				       structure: layout,
				       rowsPerPage: 20,
				       onRowClick: display,
				       sortInfo: -8,
				       sortOrder: 'ascending'
				       }, 'standingsNode' );

     this.grid.startup();
   }
   
});

})();
