% 1. Hechos: listas de items del aventurero
items_principales([espada, pocion, escudo, pocion]).  % Aridad: 1 (incluye duplicado)
items_secundarios([antorcha, mapa, cuerda]).          % Aridad: 1 (items distintos)

% 2. Recorrido recursivo del inventario
mostrar_inventario([]) :- !.                          % Caso base: lista vacia
mostrar_inventario([Cabeza|Cola]) :-                  % Caso recursivo: imprime cabeza y procesa cola
    write('- '), writeln(Cabeza),
    mostrar_inventario(Cola).

% 3. Regla principal de procesamiento
% Aridad: 5 -> procesar_inventario(ItemBuscado, TotalItems, InventarioInvertido, InventarioUnico, InventarioOrdenado)
procesar_inventario(ItemBuscado, TotalItems, InventarioInvertido, InventarioUnico, InventarioOrdenado) :-
    items_principales(Principales),
    items_secundarios(Secundarios),
    append(Principales, Secundarios, InventarioGeneral),  % append/3: une ambas listas
    length(InventarioGeneral, TotalItems),                % length/2: calcula total de items
    member(ItemBuscado, InventarioGeneral),               % member/2: verifica pertenencia del item
    reverse(InventarioGeneral, InventarioInvertido),      % reverse/2: invierte la lista
    sort(InventarioGeneral, InventarioUnico),             % sort/2: ordena y elimina duplicados
    msort(InventarioGeneral, InventarioOrdenado),         % msort/2: ordena conservando duplicados
    nl, writeln('=== MOSTRANDO INVENTARIO GENERAL (RECURSIVO) ==='),
    mostrar_inventario(InventarioGeneral).                % Llamada recursiva final

% Regla auxiliar para obtener datos completos si el item no existe
obtener_inventario_completo(TotalItems, InventarioGeneral, InventarioInvertido, InventarioUnico, InventarioOrdenado) :-
    items_principales(Principales),
    items_secundarios(Secundarios),
    append(Principales, Secundarios, InventarioGeneral),
    length(InventarioGeneral, TotalItems),
    reverse(InventarioGeneral, InventarioInvertido),
    sort(InventarioGeneral, InventarioUnico),
    msort(InventarioGeneral, InventarioOrdenado).
