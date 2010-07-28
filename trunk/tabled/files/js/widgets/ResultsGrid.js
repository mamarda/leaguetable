( function() {

dojo.provide("leaguedata.widgets.ResultsGrid");

dojo.require("dijit.dijit");
dojo.require("dojo.data.ItemFileWriteStore")
dojo.require("dojox.grid.DataGrid");

dojo.declare( "leaguedata.widgets.ResultsGrid", [dijit._Widget], {

   parentnode: null,
   gridcontainer: null,
   gridnode: null,
   grid: null,
   
   editable: false,

   constructor: function( p, gridnode, standings, editable ){
      this.parentnode = gridnode;
      this.standings = standings;      
      this.editable = editable;
   },
   
   updateStandings: function(){     				
      this.standings.reload();                   				
   },

   postCreate: function(){
     
     this.gridcontainer = document.createElement( "div" ); 

     dojo.addClass( this.gridcontainer, "gridContainer" );

     this.parentnode.appendChild( this.gridcontainer );

     this.gridnode = document.createElement( "div" ); 

     dojo.addClass( this.gridnode, "gridNode" );

     this.gridcontainer.appendChild( this.gridnode );

     this.gridnode.id = "gridNode"; 

     var jsonStore = new dojo.data.ItemFileWriteStore( { url: "/results" } );    

     var layout= [ 	{ field: "fixture", width: "60px", name: "Id", styles: 'text-align: center;' },
     				{ field: "date", width: "70px", name: "Date" },
		   			{ field: "hometeam", width: "auto", styles: 'text-align: left;', name: "Home Team" },
		   			{ field: "homescore", width: "50px", type: dojox.grid.cells.Select, options:[ '0', '1', '2', '3', '4', '5', '6', '7', '8', '9' ], styles: 'text-align: center;', name: "R" },
		   			{ field: "awayscore", width: "50px", type: dojox.grid.cells.Select, options:[ '0', '1', '2', '3', '4', '5', '6', '7', '8', '9' ], styles: 'text-align: center;', name: "R" },
		   			{ field: "awayteam", width: "auto", styles: 'text-align: left;', name: "Away Team" } ];
 
 	 layout[3].editable = this.editable;
 	 layout[4].editable = this.editable;	 
 	 
 	 var griddata = { query: { fixture: '*' },
				      store: jsonStore,
				      structure: layout,
				      rowsPerPage: 20,
				      singleClickEdit: true,
				      sortInfo: 1 }	
 
     this.grid = new dojox.grid.DataGrid( griddata, 'gridNode' );			      
				       
	 this.grid.onApplyCellEdit = function( value, rowIndex, fieldIndex ){
				       	
	    var row = this.getItem(rowIndex);
				       	
		if( row.homescore != "-" && row.awayscore != "-" ){
			
		   var newscore = '{id:' + row.fixture + ', homescore:' + row.homescore + ', awayscore:' + row.awayscore +'}'	
			
		   var xhrArgs = { url: "/results",
                		   postData: newscore,
                		   handleAs: "text",
                		   load: dojo.hitch( this, "updateStandings" ),
               			   error: function(error) {console.log( error );}
          				  } 
				       		
		   var deferred = dojo.xhrPost(xhrArgs);
		 }			       	
	 }
				       
	 this.grid.updateStandings = dojo.hitch( this, "updateStandings" );
				       
     this.grid.startup();
   }
   
});

})();
