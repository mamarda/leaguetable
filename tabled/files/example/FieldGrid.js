( function() {

dojo.provide("ajax.example.FieldGrid");

dojo.require("dijit.form.Button");
dojo.require("dijit.ColorPalette");
dojo.require("dijit.dijit");
dojo.require("dojo.data.ItemFileWriteStore")
dojo.require("dojox.grid.DataGrid");

dojo.declare( "ajax.example.FieldGrid", [dijit._Widget], {

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

     dojo.addClass( this.gridnode, "gridNode" );

     this.gridcontainer.appendChild( this.gridnode );

     this.gridnode.id = "gridNode"; 

     var jsonStore = new dojo.data.ItemFileWriteStore( { url: "results" } );
     
     selectCell = {
				styles: 'text-align: center;',
				type: dojox.grid.cells.Select
	 }; 

     var layout= [ 	{ field: "date", width: "70px", name: "Date" },
		   			{ field: "hometeam", width: "auto", styles: 'text-align: left;', name: "Home Team" },
		   			{ editable: true, field: "homescore", width: "50px",  type: dojox.grid.cells.Select, options:[ '0', '1', '2', '3', '4', '5', '6', '7', '8', '9' ], styles: 'text-align: center;', name: "R" },
		   			{ field: "awayscore", width: "50px", editable: true, type: dojox.grid.cells.Select, options:[ '0', '1', '2', '3', '4', '5', '6', '7', '8', '9' ], styles: 'text-align: center;', name: "R" },
		   			{ field: "awayteam", width: "auto", styles: 'text-align: left;', name: "Away Team" } ];
 
     this.grid = new dojox.grid.DataGrid( { query: { fixture: '*' },
				       store: jsonStore,
				       structure: layout,
				       rowsPerPage: 20,
				       singleClickEdit: true,
				       //onRowClick: display,
				       }, 'gridNode' );

     this.grid.startup();
   }
   
});

})();
