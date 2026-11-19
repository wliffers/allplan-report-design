# Report templates for Allplan 2027

Seven designed evaluations with charts, key figures, tables and part
images from your model, in German (`deu`) and English (`eng`).

## The seven templates

- **Report Master** – 10 pages of evaluation from walls, slabs, columns,
  beams, base slab, rooms, and window and door SmartParts.
- **Report Master Floor plan** – storey floor plan and room cards.
- **Report Master Room elevations** – per room the wall areas and the
  drawn room elevation.
- **Report Master Wall finishes** – plaster, paint, reveals per room.
- **Report Master Reinforcement** – bar schedule, mesh schedule, overlengths.
- **Report Master Layout list** – layouts of the project: overview, list.
- **Report Master Lists** – complete component list per type, labels with QR code to cut out.

## Setup

1. Copy the files of one language folder into your own folder among the
   office reports of Allplan 2027, for example
   `C:\allplandaten\2027\Std\Reports\eng\My reports\`
   (German: `...\Reports\deu\My reports\`).
   *Assumption:* default path; where your data lives, see the path settings.
2. Open the report dialog, pick the template in your category.

## What each template needs

- **Master, Floor plan, Wall finishes, Reinforcement, Lists:** drawing file; **Layout list:** project.
- **Wall finishes:** only rooms that have a finish.
- **Room elevations:** additionally a drawing file with the room
  elevation drawing for each room, each with a frame (thin slab,
  material "Abwicklung", designation = component ID of the room). The
  report does not draw anything itself, it shows what lies in the
  drawing file. Without such a drawing the section stays empty.

## Using the report window

In the Allplan window these are intended: click on a part, expand,
sort, and the controls on the left (prices, target window share,
minimum door width, show details). In PDF none of this works.
Tried in the Allplan window: controls, expanding and sorting work. The
click on a part (zoom into the model) is built in but not confirmed:
in the test window it had no effect.

## English templates

Texts are English, numbers use the en-US format. Names from the model
(rooms, materials) stay as they are in the project. Material groups are
recognised by German and English words (concrete, masonry, insulation,
plasterboard, timber, steel, glass, stone).

## Identifiers

Every building block carries an identifier (K010, D040 ...), index on
page 10 of the Master. With them you can order a custom report.

## Limits

- Allplan fills only the first data set of a report.
- Large projects take minutes (measured: 3,545 components, the 10-page
  master 3 to 7 minutes; Allplan shows "not responding" meanwhile).
- Room elevations: at most 8 rooms per report; a line names the rest.
- The check script reports one note each for Wall finishes and Room
  elevations, on purpose (explained in the guide, section on checking).
