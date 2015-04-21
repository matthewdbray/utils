#!/usr/bin/awk -f


BEGIN {
  minX =  10000000;
  maxX = -9999999;
  minY =  10000000;
  maxY = -9999999;
  minZ =  10000000;
  maxZ = -9999999;
  vertcount = 0;
  facecount = 0;
  fext = "";
  err = 0;
  firstLine = 1;
}

{
  if( length( fext ) == 0 ) {
    fext = getFilenameExtension( );
  }

  if( fext == "2dm" || fext == "3dm" ) {

    if ( $1 == "ND" ) {
      if ( $3 < minX ) { minX = $3; }
      if ( $3 > maxX ) { maxX = $3; }
      if ( $4 < minY ) { minY = $4; }
      if ( $4 > maxY ) { maxY = $4; }
      if ( $5 < minZ ) { minZ = $5; }
      if ( $5 > maxZ ) { maxZ = $5; }
      vertcount++;
    }
    if ( $1 == "E3T" || $1 == "E4T" ) {
      facecount++;
    }     
  }
  else if ( fext == "obj" ) {

    if ( $1 == "v" ) {
      if ( $2 < minX ) { minX = $2; }
      if ( $2 > maxX ) { maxX = $2; }
      if ( $3 < minY ) { minY = $3; }
      if ( $3 > maxY ) { maxY = $3; }
      if ( $4 < minZ ) { minZ = $4; }
      if ( $4 > maxZ ) { maxZ = $4; }
      vertcount++;
    }
    else if( $1 == "f")
      facecount++;
  }
  else if ( fext == "pts" ) {

    if ( "1" != firstLine ) {

      if ( $1 < minX ) { minX = $1; }
      if ( $1 > maxX ) { maxX = $1; }
      if ( $2 < minY ) { minY = $2; }
      if ( $2 > maxY ) { maxY = $2; }
      if ( $3 < minZ ) { minZ = $3; }
      if ( $3 > maxZ ) { maxZ = $3; }
      vertcount++;
    }
    else {
      firstLine = "0";
    }

  }
  else if ( fext == "msh" ) {

  }
  else {
    print "\nWarning: Unrecognized filename extension.  Use 2dm,3dm,obj,pts.\n";
    err = 1;
    exit;
  }

}

END {

  if( err == 1 ) exit;
  dX = maxX-minX;
  dY = maxY-minY;
  dZ = maxZ-minZ;
  ctrX = minX + (dX/2);
  ctrY = minY + (dY/2);
  ctrZ = minZ + (dZ/2);

  print "\nBounds of " fext " file " FILENAME;
  printf  " %05d vertices\n", vertcount;
  printf  " %10d Facets\n", facecount;
  printf  " X(%12.7f, %12.7f) dX %12.7f ctrX %12.8f\n", minX,maxX ,dX,ctrX;
  printf  " Y(%12.7f, %12.7f) dY %12.7f ctrY %12.8f\n", minY,maxY ,dY,ctrY;
  printf  " Z(%12.7f, %12.7f) dZ %12.7f ctrZ %12.8f\n", minZ,maxZ ,dZ,ctrZ;
}

function getFilenameExtension( )
{

  ext = index( FILENAME, "." );
  if( ext != 0 ) {
    fext = tolower( substr( FILENAME, ext+1 ) );
    ext = index( fext, "." );
    if( ext != 0 ) {
      fext = substr( fext, ext+1 );
    }
  }
  else
    fext = "";

  return fext
}
