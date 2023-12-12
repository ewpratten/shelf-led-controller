// Settings
PCB_WIDTH = 70 + 0.5;
PCB_HEIGHT = 30 + 0.5;
PCB_DEPTH = 10;
WALLS = 1.5;

difference() {
  // Case shape
  cube([
    PCB_WIDTH + (WALLS * 2), PCB_HEIGHT + (WALLS * 2), PCB_DEPTH + (WALLS * 2)
  ]);

  // Cutout for PCB
  translate([ WALLS, WALLS, WALLS ]) {
    cube([ PCB_WIDTH, PCB_HEIGHT, PCB_DEPTH ]);
  };

  // Cut an opening for the button
  translate([ WALLS + 56, WALLS+ (PCB_HEIGHT/2)-(10), WALLS ]) {
    cube([ 8, 20, 50 ]);
  }
}