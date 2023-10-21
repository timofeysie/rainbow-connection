import glowbit
import time
matrix = glowbit.matrix8x8()

def scroll_large_image():
    large_image = [
    [matrix.rgbColour(71, 90, 28), matrix.rgbColour(80, 99, 31), matrix.rgbColour(89, 107, 41), matrix.rgbColour(78, 94, 38), matrix.rgbColour(95, 106, 53), matrix.rgbColour(128, 162, 59), matrix.rgbColour(151, 177, 69), matrix.rgbColour(157, 179, 69), ],
    [matrix.rgbColour(100, 117, 43), matrix.rgbColour(96, 113, 49), matrix.rgbColour(76, 97, 42), matrix.rgbColour(60, 79, 30), matrix.rgbColour(128, 132, 73), matrix.rgbColour(128, 162, 59), matrix.rgbColour(151, 178, 68), matrix.rgbColour(158, 181, 68), ],
    [matrix.rgbColour(99, 117, 71), matrix.rgbColour(111, 130, 104), matrix.rgbColour(104, 121, 92), matrix.rgbColour(119, 104, 76), matrix.rgbColour(115, 115, 59), matrix.rgbColour(134, 166, 64), matrix.rgbColour(152, 178, 70), matrix.rgbColour(161, 183, 71), ],
    [matrix.rgbColour(157, 179, 207), matrix.rgbColour(170, 187, 206), matrix.rgbColour(77, 90, 65), matrix.rgbColour(48, 50, 20), matrix.rgbColour(96, 100, 51), matrix.rgbColour(139, 172, 70), matrix.rgbColour(152, 178, 69), matrix.rgbColour(157, 181, 70), ],
    [matrix.rgbColour(149, 172, 202), matrix.rgbColour(145, 162, 173), matrix.rgbColour(78, 86, 42), matrix.rgbColour(61, 69, 34), matrix.rgbColour(80, 86, 43), matrix.rgbColour(137, 168, 68), matrix.rgbColour(152, 179, 71), matrix.rgbColour(159, 182, 73), ],
    [matrix.rgbColour(136, 163, 196), matrix.rgbColour(149, 172, 196), matrix.rgbColour(120, 134, 124), matrix.rgbColour(81, 90, 49), matrix.rgbColour(83, 83, 65), matrix.rgbColour(142, 170, 70), matrix.rgbColour(152, 179, 69), matrix.rgbColour(160, 184, 73), ],
    [matrix.rgbColour(139, 165, 197), matrix.rgbColour(153, 175, 201), matrix.rgbColour(132, 144, 147), matrix.rgbColour(85, 99, 37), matrix.rgbColour(63, 55, 34), matrix.rgbColour(140, 165, 66), matrix.rgbColour(154, 182, 70), matrix.rgbColour(160, 183, 73), ],
    [matrix.rgbColour(137, 165, 193), matrix.rgbColour(125, 151, 175), matrix.rgbColour(94, 106, 84), matrix.rgbColour(91, 101, 57), matrix.rgbColour(119, 117, 104), matrix.rgbColour(137, 161, 64), matrix.rgbColour(155, 182, 70), matrix.rgbColour(159, 182, 72), ],
    [matrix.rgbColour(132, 159, 189), matrix.rgbColour(128, 154, 177), matrix.rgbColour(90, 102, 75), matrix.rgbColour(98, 106, 67), matrix.rgbColour(77, 67, 25), matrix.rgbColour(137, 159, 66), matrix.rgbColour(154, 181, 69), matrix.rgbColour(157, 182, 71), ],
    [matrix.rgbColour(133, 159, 190), matrix.rgbColour(132, 159, 188), matrix.rgbColour(137, 150, 156), matrix.rgbColour(102, 107, 72), matrix.rgbColour(79, 78, 24), matrix.rgbColour(138, 157, 70), matrix.rgbColour(152, 181, 72), matrix.rgbColour(155, 183, 73), ],
    [matrix.rgbColour(137, 161, 192), matrix.rgbColour(140, 163, 191), matrix.rgbColour(122, 138, 146), matrix.rgbColour(84, 91, 69), matrix.rgbColour(68, 76, 48), matrix.rgbColour(143, 161, 89), matrix.rgbColour(150, 180, 72), matrix.rgbColour(154, 181, 73), ],
    [matrix.rgbColour(140, 164, 190), matrix.rgbColour(148, 170, 192), matrix.rgbColour(106, 122, 121), matrix.rgbColour(92, 105, 49), matrix.rgbColour(72, 84, 44), matrix.rgbColour(132, 154, 73), matrix.rgbColour(147, 177, 74), matrix.rgbColour(146, 175, 69), ],
    [matrix.rgbColour(99, 116, 113), matrix.rgbColour(76, 89, 63), matrix.rgbColour(53, 67, 31), matrix.rgbColour(82, 95, 40), matrix.rgbColour(80, 93, 45), matrix.rgbColour(132, 156, 65), matrix.rgbColour(146, 178, 74), matrix.rgbColour(148, 176, 69), ],
    [matrix.rgbColour(79, 95, 81), matrix.rgbColour(90, 106, 90), matrix.rgbColour(57, 73, 41), matrix.rgbColour(47, 60, 28), matrix.rgbColour(60, 79, 29), matrix.rgbColour(125, 148, 65), matrix.rgbColour(149, 181, 75), matrix.rgbColour(153, 181, 71), ],
    [matrix.rgbColour(98, 116, 95), matrix.rgbColour(82, 100, 76), matrix.rgbColour(65, 83, 39), matrix.rgbColour(63, 81, 37), matrix.rgbColour(65, 81, 34), matrix.rgbColour(110, 135, 53), matrix.rgbColour(148, 181, 72), matrix.rgbColour(147, 177, 66), ],
    [matrix.rgbColour(123, 140, 144), matrix.rgbColour(122, 137, 144), matrix.rgbColour(106, 123, 108), matrix.rgbColour(94, 106, 82), matrix.rgbColour(74, 83, 62), matrix.rgbColour(107, 129, 55), matrix.rgbColour(150, 181, 73), matrix.rgbColour(146, 177, 68), ],
    [matrix.rgbColour(128, 143, 147), matrix.rgbColour(105, 120, 108), matrix.rgbColour(86, 101, 67), matrix.rgbColour(71, 86, 53), matrix.rgbColour(74, 86, 65), matrix.rgbColour(95, 119, 49), matrix.rgbColour(144, 178, 73), matrix.rgbColour(143, 176, 67), ],
    [matrix.rgbColour(166, 189, 213), matrix.rgbColour(149, 174, 201), matrix.rgbColour(137, 157, 170), matrix.rgbColour(100, 105, 101), matrix.rgbColour(151, 160, 157), matrix.rgbColour(85, 105, 47), matrix.rgbColour(144, 177, 74), matrix.rgbColour(142, 177, 68), ],
    [matrix.rgbColour(175, 194, 218), matrix.rgbColour(153, 177, 202), matrix.rgbColour(151, 169, 188), matrix.rgbColour(163, 171, 172), matrix.rgbColour(176, 185, 183), matrix.rgbColour(82, 100, 56), matrix.rgbColour(150, 181, 76), matrix.rgbColour(147, 179, 68), ],
    [matrix.rgbColour(179, 199, 220), matrix.rgbColour(161, 183, 207), matrix.rgbColour(154, 176, 199), matrix.rgbColour(150, 163, 164), matrix.rgbColour(188, 197, 200), matrix.rgbColour(120, 131, 106), matrix.rgbColour(145, 176, 75), matrix.rgbColour(151, 180, 69), ],
    [matrix.rgbColour(165, 187, 211), matrix.rgbColour(166, 188, 211), matrix.rgbColour(166, 185, 203), matrix.rgbColour(99, 109, 100), matrix.rgbColour(147, 156, 146), matrix.rgbColour(128, 139, 112), matrix.rgbColour(139, 172, 73), matrix.rgbColour(143, 173, 68), ],
    [matrix.rgbColour(136, 161, 192), matrix.rgbColour(152, 177, 204), matrix.rgbColour(167, 188, 211), matrix.rgbColour(108, 119, 119), matrix.rgbColour(150, 159, 97), matrix.rgbColour(93, 113, 43), matrix.rgbColour(137, 167, 73), matrix.rgbColour(140, 172, 71), ],
    [matrix.rgbColour(148, 173, 198), matrix.rgbColour(156, 180, 203), matrix.rgbColour(173, 194, 214), matrix.rgbColour(66, 74, 52), matrix.rgbColour(137, 145, 74), matrix.rgbColour(68, 86, 30), matrix.rgbColour(138, 164, 71), matrix.rgbColour(136, 168, 64), ],
    [matrix.rgbColour(169, 191, 215), matrix.rgbColour(159, 181, 205), matrix.rgbColour(163, 186, 208), matrix.rgbColour(82, 98, 78), matrix.rgbColour(128, 134, 71), matrix.rgbColour(64, 82, 31), matrix.rgbColour(134, 159, 67), matrix.rgbColour(148, 177, 68), ],
    [matrix.rgbColour(171, 192, 216), matrix.rgbColour(166, 186, 211), matrix.rgbColour(157, 181, 206), matrix.rgbColour(103, 117, 117), matrix.rgbColour(127, 133, 75), matrix.rgbColour(86, 103, 32), matrix.rgbColour(132, 156, 69), matrix.rgbColour(148, 174, 63), ],
    [matrix.rgbColour(154, 177, 202), matrix.rgbColour(168, 189, 212), matrix.rgbColour(162, 184, 208), matrix.rgbColour(133, 150, 152), matrix.rgbColour(128, 139, 78), matrix.rgbColour(141, 171, 76), matrix.rgbColour(135, 160, 65), matrix.rgbColour(150, 175, 63), ],
    [matrix.rgbColour(165, 187, 210), matrix.rgbColour(164, 186, 210), matrix.rgbColour(169, 190, 213), matrix.rgbColour(153, 172, 184), matrix.rgbColour(110, 122, 68), matrix.rgbColour(152, 183, 81), matrix.rgbColour(137, 161, 65), matrix.rgbColour(147, 175, 65), ],
    [matrix.rgbColour(158, 180, 204), matrix.rgbColour(162, 185, 209), matrix.rgbColour(175, 195, 218), matrix.rgbColour(169, 191, 206), matrix.rgbColour(91, 107, 76), matrix.rgbColour(152, 183, 86), matrix.rgbColour(138, 164, 70), matrix.rgbColour(146, 174, 66), ],
    [matrix.rgbColour(159, 181, 205), matrix.rgbColour(171, 192, 213), matrix.rgbColour(174, 194, 217), matrix.rgbColour(171, 193, 212), matrix.rgbColour(85, 106, 95), matrix.rgbColour(145, 175, 83), matrix.rgbColour(139, 167, 71), matrix.rgbColour(144, 174, 68), ],
    [matrix.rgbColour(162, 183, 207), matrix.rgbColour(187, 205, 223), matrix.rgbColour(176, 197, 220), matrix.rgbColour(172, 195, 214), matrix.rgbColour(81, 102, 95), matrix.rgbColour(129, 159, 82), matrix.rgbColour(137, 166, 71), matrix.rgbColour(145, 175, 71), ],
    [matrix.rgbColour(172, 191, 214), matrix.rgbColour(196, 213, 229), matrix.rgbColour(180, 201, 223), matrix.rgbColour(166, 190, 209), matrix.rgbColour(78, 99, 93), matrix.rgbColour(144, 175, 90), matrix.rgbColour(141, 173, 73), matrix.rgbColour(137, 170, 67), ],
    [matrix.rgbColour(189, 206, 226), matrix.rgbColour(197, 214, 230), matrix.rgbColour(179, 200, 222), matrix.rgbColour(175, 199, 218), matrix.rgbColour(88, 110, 99), matrix.rgbColour(151, 179, 97), matrix.rgbColour(140, 172, 72), matrix.rgbColour(132, 166, 66), ],
    [matrix.rgbColour(197, 214, 232), matrix.rgbColour(198, 215, 231), matrix.rgbColour(177, 199, 221), matrix.rgbColour(176, 201, 221), matrix.rgbColour(108, 127, 119), matrix.rgbColour(156, 181, 98), matrix.rgbColour(141, 172, 70), matrix.rgbColour(130, 165, 64), ],
    [matrix.rgbColour(205, 219, 235), matrix.rgbColour(202, 218, 233), matrix.rgbColour(176, 198, 220), matrix.rgbColour(178, 202, 223), matrix.rgbColour(123, 145, 150), matrix.rgbColour(151, 177, 96), matrix.rgbColour(143, 174, 70), matrix.rgbColour(131, 164, 63), ],
    [matrix.rgbColour(198, 215, 236), matrix.rgbColour(198, 215, 232), matrix.rgbColour(178, 199, 222), matrix.rgbColour(173, 197, 221), matrix.rgbColour(137, 160, 168), matrix.rgbColour(145, 170, 87), matrix.rgbColour(143, 173, 72), matrix.rgbColour(131, 165, 64), ],
    [matrix.rgbColour(194, 212, 233), matrix.rgbColour(190, 208, 228), matrix.rgbColour(172, 195, 218), matrix.rgbColour(174, 198, 221), matrix.rgbColour(128, 148, 155), matrix.rgbColour(151, 176, 96), matrix.rgbColour(141, 171, 70), matrix.rgbColour(131, 165, 66), ],
    [matrix.rgbColour(180, 200, 223), matrix.rgbColour(194, 211, 230), matrix.rgbColour(181, 201, 221), matrix.rgbColour(181, 203, 224), matrix.rgbColour(109, 127, 127), matrix.rgbColour(156, 181, 103), matrix.rgbColour(144, 172, 73), matrix.rgbColour(127, 162, 62), ],
    [matrix.rgbColour(181, 200, 223), matrix.rgbColour(187, 206, 229), matrix.rgbColour(187, 205, 228), matrix.rgbColour(187, 209, 230), matrix.rgbColour(92, 111, 95), matrix.rgbColour(162, 184, 102), matrix.rgbColour(149, 175, 76), matrix.rgbColour(129, 161, 62), ],
    [matrix.rgbColour(189, 207, 228), matrix.rgbColour(181, 201, 225), matrix.rgbColour(174, 196, 220), matrix.rgbColour(171, 194, 209), matrix.rgbColour(49, 67, 60), matrix.rgbColour(157, 181, 96), matrix.rgbColour(147, 173, 73), matrix.rgbColour(127, 159, 61), ],
    [matrix.rgbColour(199, 215, 236), matrix.rgbColour(177, 199, 223), matrix.rgbColour(171, 194, 218), matrix.rgbColour(171, 194, 211), matrix.rgbColour(64, 84, 67), matrix.rgbColour(157, 181, 94), matrix.rgbColour(141, 167, 72), matrix.rgbColour(123, 157, 57), ],
    [matrix.rgbColour(202, 219, 236), matrix.rgbColour(182, 203, 226), matrix.rgbColour(170, 194, 218), matrix.rgbColour(170, 192, 208), matrix.rgbColour(63, 82, 66), matrix.rgbColour(158, 181, 95), matrix.rgbColour(113, 139, 66), matrix.rgbColour(123, 154, 61), ],
    [matrix.rgbColour(211, 225, 239), matrix.rgbColour(194, 211, 231), matrix.rgbColour(175, 198, 221), matrix.rgbColour(171, 192, 207), matrix.rgbColour(56, 74, 61), matrix.rgbColour(161, 184, 96), matrix.rgbColour(143, 171, 72), matrix.rgbColour(121, 154, 60), ],
    [matrix.rgbColour(215, 228, 241), matrix.rgbColour(193, 211, 230), matrix.rgbColour(177, 199, 221), matrix.rgbColour(165, 188, 200), matrix.rgbColour(54, 72, 60), matrix.rgbColour(162, 185, 99), matrix.rgbColour(149, 175, 77), matrix.rgbColour(119, 155, 56), ],
    [matrix.rgbColour(216, 228, 241), matrix.rgbColour(194, 212, 230), matrix.rgbColour(188, 206, 227), matrix.rgbColour(160, 180, 190), matrix.rgbColour(41, 60, 53), matrix.rgbColour(159, 183, 100), matrix.rgbColour(149, 175, 76), matrix.rgbColour(122, 157, 55), ],
    [matrix.rgbColour(219, 229, 241), matrix.rgbColour(198, 214, 230), matrix.rgbColour(192, 211, 230), matrix.rgbColour(159, 176, 181), matrix.rgbColour(64, 85, 64), matrix.rgbColour(156, 182, 97), matrix.rgbColour(147, 174, 75), matrix.rgbColour(125, 159, 52), ],
    [matrix.rgbColour(227, 234, 243), matrix.rgbColour(211, 223, 236), matrix.rgbColour(188, 207, 227), matrix.rgbColour(148, 165, 173), matrix.rgbColour(75, 94, 72), matrix.rgbColour(148, 174, 86), matrix.rgbColour(147, 174, 74), matrix.rgbColour(128, 159, 53), ],
    [matrix.rgbColour(232, 238, 245), matrix.rgbColour(210, 222, 236), matrix.rgbColour(190, 207, 227), matrix.rgbColour(155, 172, 180), matrix.rgbColour(74, 95, 74), matrix.rgbColour(155, 180, 90), matrix.rgbColour(147, 173, 74), matrix.rgbColour(131, 162, 56), ],
    [matrix.rgbColour(233, 238, 244), matrix.rgbColour(214, 226, 238), matrix.rgbColour(195, 212, 227), matrix.rgbColour(164, 181, 191), matrix.rgbColour(56, 69, 66), matrix.rgbColour(162, 186, 94), matrix.rgbColour(144, 171, 72), matrix.rgbColour(134, 164, 58), ],
    [matrix.rgbColour(227, 235, 243), matrix.rgbColour(213, 225, 237), matrix.rgbColour(201, 216, 232), matrix.rgbColour(181, 198, 211), matrix.rgbColour(61, 75, 69), matrix.rgbColour(155, 176, 93), matrix.rgbColour(138, 165, 70), matrix.rgbColour(135, 165, 59), ],
    [matrix.rgbColour(205, 219, 234), matrix.rgbColour(208, 222, 236), matrix.rgbColour(199, 215, 231), matrix.rgbColour(198, 215, 230), matrix.rgbColour(117, 130, 126), matrix.rgbColour(161, 185, 92), matrix.rgbColour(136, 167, 70), matrix.rgbColour(137, 164, 56), ],
    [matrix.rgbColour(207, 222, 237), matrix.rgbColour(203, 218, 233), matrix.rgbColour(196, 213, 230), matrix.rgbColour(198, 215, 232), matrix.rgbColour(119, 136, 139), matrix.rgbColour(159, 182, 93), matrix.rgbColour(88, 109, 56), matrix.rgbColour(135, 163, 60), ],
    [matrix.rgbColour(204, 220, 236), matrix.rgbColour(199, 216, 232), matrix.rgbColour(193, 210, 230), matrix.rgbColour(197, 214, 229), matrix.rgbColour(127, 143, 147), matrix.rgbColour(148, 170, 93), matrix.rgbColour(63, 84, 43), matrix.rgbColour(136, 163, 60), ],
    [matrix.rgbColour(201, 218, 235), matrix.rgbColour(182, 203, 225), matrix.rgbColour(200, 217, 232), matrix.rgbColour(192, 212, 230), matrix.rgbColour(139, 158, 163), matrix.rgbColour(37, 51, 38), matrix.rgbColour(10, 24, 14), matrix.rgbColour(138, 165, 61), ],
    [matrix.rgbColour(206, 222, 239), matrix.rgbColour(190, 209, 229), matrix.rgbColour(194, 212, 230), matrix.rgbColour(195, 215, 232), matrix.rgbColour(145, 165, 170), matrix.rgbColour(72, 90, 56), matrix.rgbColour(41, 57, 30), matrix.rgbColour(139, 165, 58), ],
    [matrix.rgbColour(215, 228, 242), matrix.rgbColour(197, 214, 231), matrix.rgbColour(200, 216, 232), matrix.rgbColour(196, 215, 232), matrix.rgbColour(144, 165, 171), matrix.rgbColour(67, 77, 57), matrix.rgbColour(18, 33, 20), matrix.rgbColour(142, 167, 61), ],
    [matrix.rgbColour(231, 239, 247), matrix.rgbColour(206, 221, 235), matrix.rgbColour(204, 220, 235), matrix.rgbColour(143, 159, 163), matrix.rgbColour(47, 62, 53), matrix.rgbColour(21, 34, 24), matrix.rgbColour(36, 48, 37), matrix.rgbColour(140, 165, 59), ],
    [matrix.rgbColour(242, 245, 250), matrix.rgbColour(218, 229, 240), matrix.rgbColour(215, 226, 237), matrix.rgbColour(193, 210, 225), matrix.rgbColour(93, 104, 106), matrix.rgbColour(34, 46, 34), matrix.rgbColour(15, 26, 22), matrix.rgbColour(142, 165, 59), ],
    [matrix.rgbColour(248, 249, 252), matrix.rgbColour(240, 244, 249), matrix.rgbColour(226, 233, 242), matrix.rgbColour(171, 186, 198), matrix.rgbColour(30, 41, 35), matrix.rgbColour(33, 44, 33), matrix.rgbColour(18, 26, 26), matrix.rgbColour(147, 168, 62), ],
    [matrix.rgbColour(251, 251, 253), matrix.rgbColour(252, 252, 253), matrix.rgbColour(224, 232, 241), matrix.rgbColour(175, 189, 195), matrix.rgbColour(33, 45, 35), matrix.rgbColour(36, 53, 32), matrix.rgbColour(18, 32, 20), matrix.rgbColour(146, 169, 63), ],
    [matrix.rgbColour(242, 246, 250), matrix.rgbColour(238, 243, 249), matrix.rgbColour(215, 227, 238), matrix.rgbColour(196, 213, 226), matrix.rgbColour(78, 91, 87), matrix.rgbColour(44, 60, 40), matrix.rgbColour(33, 49, 23), matrix.rgbColour(150, 172, 62), ],
    [matrix.rgbColour(240, 245, 249), matrix.rgbColour(228, 237, 244), matrix.rgbColour(212, 226, 238), matrix.rgbColour(133, 144, 149), matrix.rgbColour(17, 30, 28), matrix.rgbColour(19, 32, 25), matrix.rgbColour(7, 21, 15), matrix.rgbColour(158, 180, 64), ],
    [matrix.rgbColour(227, 236, 245), matrix.rgbColour(231, 239, 246), matrix.rgbColour(213, 224, 233), matrix.rgbColour(62, 72, 72), matrix.rgbColour(26, 38, 33), matrix.rgbColour(21, 34, 28), matrix.rgbColour(20, 29, 15), matrix.rgbColour(169, 191, 70), ],
    [matrix.rgbColour(223, 233, 243), matrix.rgbColour(224, 235, 244), matrix.rgbColour(204, 208, 210), matrix.rgbColour(23, 36, 34), matrix.rgbColour(29, 43, 39), matrix.rgbColour(15, 27, 25), matrix.rgbColour(67, 76, 39), matrix.rgbColour(164, 185, 59), ]]

    print("Converted large_image:", large_image) # Debugging line

    # Function to draw a section of the large image on the matrix
    def draw_section(section):
        print("Drawing section:", section) # Debugging line
        matrix.pixelsFill(matrix.black())
        row = 0
        col = 0
        for r in section:
            for c in r:
                matrix.pixelSetXY(col, row, c)
                col += 1
                if (col > 7):
                    col = 0
            row += 1
        matrix.pixelsShow()

    # Scroll through the large image one column at a time
    for i in range(len(large_image) - 7):
        print("Scrolling to column:", i) # Debugging line
        section = large_image[i:i+8]
        draw_section(section)
        time.sleep(0.6) # Add a delay of 0.1 seconds

def regular():
    print("regular")
    matrix.pixelsFill(matrix.black())
    T = [[0, 0, 1, 1, 1, 1, 0, 0],
         [0, 1, 0, 0, 0, 0, 1, 0],
         [1, 0, 1, 0, 0, 1, 0, 1],
         [1, 0, 0, 0, 0, 0, 0, 1],
         [1, 0, 1, 1, 1, 1, 0, 1],
         [1, 0, 0, 0, 0, 0, 0, 1],
         [0, 1, 0, 0, 0, 0, 1, 0],
         [0, 0, 1, 1, 1, 1, 0, 0]]
    row = 0
    col = 0
    for r in T:
        for c in r:
            color = matrix.black()
            if (c > 0):
                color = matrix.white()
            matrix.pixelSetXY(col, row, color)
            col += 1
            if (col > 7):
                col = 0
        row += 1
    matrix.pixelsShow()
def sad():
    print("sad")
    T = [[0, 0, 1, 1, 1, 1, 0, 0],
            [0, 1, 0, 0, 0, 0, 1, 0],
            [1, 0, 1, 0, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 1, 1, 0, 0, 1],
            [1, 0, 1, 0, 0, 1, 0, 1],
            [0, 1, 0, 0, 0, 0, 1, 0],
            [0, 0, 1, 1, 1, 1, 0, 0]]
    row = 0
    col = 0
    for r in T:
        for c in r:
            color = matrix.black()
            if (c > 0):
                color = matrix.white()
            matrix.pixelSetXY(col, row, color)
            col += 1
            if (col > 7):
                col = 0
        row += 1
    matrix.pixelsShow()
def happy():
    matrix.pixelsFill(matrix.black())
    T = [[0, 0, 1, 1, 1, 1, 0, 0],
         [0, 1, 0, 0, 0, 0, 1, 0],
         [1, 0, 1, 0, 0, 1, 0, 1],
         [1, 0, 0, 0, 0, 0, 0, 1],
         [1, 0, 1, 0, 0, 1, 0, 1],
         [1, 0, 0, 1, 1, 0, 0, 1],
         [0, 1, 0, 0, 0, 0, 1, 0],
         [0, 0, 1, 1, 1, 1, 0, 0]]
    row = 0
    col = 0
    for r in T:
        for c in r:
            color = matrix.black()
            if (c > 0):
                color = matrix.white()
            matrix.pixelSetXY(col, row, color)
            col += 1
            if (col > 7):
                col = 0
        row += 1
    matrix.pixelsShow()
def thickLips():
    matrix.pixelsFill(matrix.black())
    T = [[0, 0, 1, 1, 1, 1, 0, 0],
         [0, 1, 0, 0, 0, 0, 1, 0],
         [1, 0, 1, 0, 0, 1, 0, 1],
         [1, 0, 0, 0, 0, 0, 0, 1],
         [1, 0, 1, 1, 1, 1, 0, 1],
         [1, 0, 1, 1, 1, 1, 0, 1],
         [0, 1, 0, 0, 0, 0, 1, 0],
         [0, 0, 1, 1, 1, 1, 0, 0]]
    row = 0
    col = 0
    for r in T:
        for c in r:
            color = matrix.black()
            if (c > 0):
                color = matrix.white()
            matrix.pixelSetXY(col, row, color)
            col += 1
            if (col > 7):
                col = 0
        row += 1
    matrix.pixelsShow()
def wry():
    print("wry")
    matrix.pixelsFill(matrix.black())
    T = [[0, 0, 1, 1, 1, 1, 0, 0],
         [0, 1, 0, 0, 0, 0, 1, 0],
         [1, 0, 1, 0, 1, 0, 0, 1],
         [1, 0, 1, 0, 1, 0, 0, 1],
         [1, 0, 0, 0, 0, 1, 0, 1],
         [1, 0, 1, 1, 1, 0, 0, 1],
         [0, 1, 0, 0, 0, 0, 1, 0],
         [0, 0, 1, 1, 1, 1, 0, 0]]
    row = 0
    col = 0
    for r in T:
        for c in r:
            color = matrix.black()
            if (c > 0):
                color = matrix.white()
            matrix.pixelSetXY(col, row, color)
            col += 1
            if (col > 7):
                col = 0
        row += 1
    matrix.pixelsShow()
def heartBounce():
    print("heart bounce")
    matrix.pixelsFill(matrix.black())
    T = [[0, 1, 1, 0, 0, 1, 1, 0],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]]
    row = 0
    col = 0
    for r in T:
        for c in r:
            color = matrix.black()
            if (c > 0):
                color = matrix.red()
            matrix.pixelSetXY(col, row, color)
            col += 1
            if (col > 7):
                col = 0
        row += 1
    matrix.pixelsShow()
    time.sleep(1)
    T = [[0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 0, 0, 1, 1, 0],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0]]
    row = 0
    col = 0
    for r in T:
        for c in r:
            color = matrix.black()
            if (c > 0):
                color = matrix.red()
            matrix.pixelSetXY(col, row, color)
            col += 1
            if (col > 7):
                col = 0
        row += 1
    matrix.pixelsShow()
    time.sleep(1)
    T = [[0, 1, 1, 0, 0, 1, 1, 0],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]]
    row = 0
    col = 0
    for r in T:
        for c in r:
            color = matrix.black()
            if (c > 0):
                color = matrix.red()
            matrix.pixelSetXY(col, row, color)
            col += 1
            if (col > 7):
                col = 0
        row += 1
    matrix.pixelsShow()
def finn():
    print("finn the human")
    matrix.pixelsFill(matrix.black())
    T = [[matrix.rgbColour(64,196,254), matrix.rgbColour(64,196,254), matrix.rgbColour(255,255,255), matrix.rgbColour(64,196,254), matrix.rgbColour(64,196,254), matrix.rgbColour(64,196,254), matrix.rgbColour(255,255,255), matrix.rgbColour(64,196,254)],
            [matrix.rgbColour(64,196,254), matrix.rgbColour(64,196,254), matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(64,196,254)],
            [matrix.rgbColour(64,196,254), matrix.rgbColour(64,196,254), matrix.rgbColour(255,255,255), matrix.rgbColour(0,0,0), matrix.rgbColour(250,220,100), matrix.rgbColour(250,220,100), matrix.rgbColour(0,0,0), matrix.rgbColour(64,196,254)],
            [matrix.rgbColour(134,188,70), matrix.rgbColour(121,173,65), matrix.rgbColour(255,255,255), matrix.rgbColour(250,220,100), matrix.rgbColour(250,220,100), matrix.rgbColour(250,220,100), matrix.rgbColour(250,220,100), matrix.rgbColour(64,196,254)],
            [matrix.rgbColour(24,88,28), matrix.rgbColour(164,199,122), matrix.rgbColour(121,197,233), matrix.rgbColour(31,140,226), matrix.rgbColour(31,140,226), matrix.rgbColour(31,140,226), matrix.rgbColour(31,140,226), matrix.rgbColour(64,196,254)],
            [matrix.rgbColour(250,220,100), matrix.rgbColour(24,88,28), matrix.rgbColour(31,140,226), matrix.rgbColour(31,140,226), matrix.rgbColour(31,140,226), matrix.rgbColour(31,140,226), matrix.rgbColour(31,140,226), matrix.rgbColour(250,220,100)],
            [matrix.rgbColour(100,216,2), matrix.rgbColour(100,216,2), matrix.rgbColour(11,61,138), matrix.rgbColour(11,61,138), matrix.rgbColour(11,61,138), matrix.rgbColour(11,61,138), matrix.rgbColour(11,61,138), matrix.rgbColour(100,216,2)],
            [matrix.rgbColour(100,216,2), matrix.rgbColour(100,216,2), matrix.rgbColour(250,220,100), matrix.rgbColour(100,216,2), matrix.rgbColour(100,216,2), matrix.rgbColour(100,216,2), matrix.rgbColour(250,220,100), matrix.rgbColour(100,216,2)]]
    row = 0
    col = 0
    for r in T:
        for c in r:
            color = matrix.black()
            matrix.pixelSetXY(col, row, c)
            col += 1
            if (col > 7):
                col = 0
        row += 1
    matrix.pixelsShow()
    time.sleep(0.5)
def angry():
    print("angry")
    matrix.pixelsFill(matrix.black())
    T = [[matrix.rgbColour(255,0,0),    matrix.rgbColour(0,0,0),      matrix.rgbColour(255,0,0),     matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0),     matrix.rgbColour(0,0,0),       matrix.rgbColour(255,0,0)],
            [matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0),    matrix.rgbColour(0,0,0),       matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0), matrix.rgbColour(0,0,0),       matrix.rgbColour(255,0,0),     matrix.rgbColour(255,0,0)],
            [matrix.rgbColour(255,0,0), matrix.rgbColour(64,196,254), matrix.rgbColour(255,255,255), matrix.rgbColour(0,0,0),   matrix.rgbColour(0,0,0),   matrix.rgbColour(64,196,253),  matrix.rgbColour(255,255,255), matrix.rgbColour(255,0,0)],
            [matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0),    matrix.rgbColour(255,0,0),     matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0),     matrix.rgbColour(255,0,0),     matrix.rgbColour(255,0,0)],
            [matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0),    matrix.rgbColour(255,0,0),     matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0),     matrix.rgbColour(255,0,0),     matrix.rgbColour(255,0,0)],
            [matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0),    matrix.rgbColour(0,0,0),       matrix.rgbColour(0,0,0),   matrix.rgbColour(0,0,0),   matrix.rgbColour(0,0,0),       matrix.rgbColour(255,0,0),     matrix.rgbColour(255,0,0)],
            [matrix.rgbColour(255,0,0), matrix.rgbColour(0,0,0),      matrix.rgbColour(255,0,0),     matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0),     matrix.rgbColour(0,0,0),       matrix.rgbColour(255,0,0)],
            [matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0),    matrix.rgbColour(255,0,0),     matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0),     matrix.rgbColour(255,0,0),     matrix.rgbColour(255,0,0)]]
    row = 0
    col = 0
    for r in T:
        for c in r:
            color = matrix.black()
            matrix.pixelSetXY(col, row, c)
            col += 1
            if (col > 7):
                col = 0
        row += 1
    matrix.pixelsShow()
def greenMonster():
    print("green monster")
    matrix.pixelsFill(matrix.black())
    T = [[matrix.rgbColour(0,0,0),      matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),       matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),       matrix.rgbColour(0,0,0)],
            [matrix.rgbColour(0,255,0), matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),       matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),       matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0)],
            [matrix.rgbColour(0,255,0), matrix.rgbColour(255,0,0),     matrix.rgbColour(0,255,0),       matrix.rgbColour(0,255,0),     matrix.rgbColour(255,0,0),     matrix.rgbColour(0,255,0),  matrix.rgbColour(0,255,0), matrix.rgbColour(0,255,0)],
            [matrix.rgbColour(0,255,0), matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),       matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0)],
            [matrix.rgbColour(0,255,0), matrix.rgbColour(0,255,0),     matrix.rgbColour(255,255,255),   matrix.rgbColour(0,0,0),       matrix.rgbColour(255,255,255), matrix.rgbColour(0,0,0),     matrix.rgbColour(255,255,255),     matrix.rgbColour(0,255,0)],
            [matrix.rgbColour(0,255,0), matrix.rgbColour(0,0,0),       matrix.rgbColour(0,0,0),         matrix.rgbColour(0,0,0),       matrix.rgbColour(0,0,0),       matrix.rgbColour(0,0,0),       matrix.rgbColour(0,0,0),     matrix.rgbColour(0,255,0)],
            [matrix.rgbColour(0,255,0), matrix.rgbColour(255,255,255), matrix.rgbColour(0,0,0),         matrix.rgbColour(255,255,255), matrix.rgbColour(0,0,0),       matrix.rgbColour(255,255,255),     matrix.rgbColour(0,0,0),       matrix.rgbColour(0,255,0)],
            [matrix.rgbColour(0,255,0), matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),       matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0)]]
    row = 0
    col = 0
    for r in T:
        for c in r:
            color = matrix.black()
            matrix.pixelSetXY(col, row, c)
            col += 1
            if (col > 7):
                col = 0
        row += 1
    matrix.pixelsShow()
def pikachu():
    print("7. pikachu")
    matrix.pixelsFill(matrix.black())
    T = [[matrix.rgbColour(255,255,255), matrix.rgbColour(66, 66, 66), matrix.rgbColour(66,66,66), matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(64,66,66)],
            [matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(255,236,60), matrix.rgbColour(255,152,0), matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(255,152,0)],
            [matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(255,236,60), matrix.rgbColour(255,236,60), matrix.rgbColour(250,220,100), matrix.rgbColour(255,236,60), matrix.rgbColour(255,152,0)],
            [matrix.rgbColour(255,152,0), matrix.rgbColour(255,152,0), matrix.rgbColour(255,255,255), matrix.rgbColour(250,220,100), matrix.rgbColour(0,0,0), matrix.rgbColour(250,220,100), matrix.rgbColour(250,220,100), matrix.rgbColour(0,0,0)],
            [matrix.rgbColour(255,152,0), matrix.rgbColour(255,152,0), matrix.rgbColour(255,255,255), matrix.rgbColour(234,30,4), matrix.rgbColour(254,241,0), matrix.rgbColour(254,241,0), matrix.rgbColour(254,241,0), matrix.rgbColour(255,152,0)],
            [matrix.rgbColour(255,255,255), matrix.rgbColour(162,89,0), matrix.rgbColour(255,255,255), matrix.rgbColour(254,241,0), matrix.rgbColour(230,137,0), matrix.rgbColour(254,241,0), matrix.rgbColour(255,152,0), matrix.rgbColour(255,255,255)],
            [matrix.rgbColour(255,255,255), matrix.rgbColour(176,97,0), matrix.rgbColour(250,238,0), matrix.rgbColour(255,152,0), matrix.rgbColour(251,238,0), matrix.rgbColour(162,89,0), matrix.rgbColour(251,238,0), matrix.rgbColour(255,255,255)],
            [matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(250,238,0), matrix.rgbColour(210,123,0), matrix.rgbColour(162,89,0), matrix.rgbColour(177,98,0), matrix.rgbColour(177,98,0), matrix.rgbColour(255,255,255)]]
    row = 0
    col = 0
    for r in T:
        for c in r:
            color = matrix.black()
            matrix.pixelSetXY(col, row, c)
            col += 1
            if (col > 7):
                col = 0
        row += 1
    matrix.pixelsShow()

def crab():
    print("crab")
    matrix.pixelsFill(matrix.black())
    T = [[   matrix.rgbColour(0,0,0),   matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(0,0,0),   matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(0,0,0),    matrix.rgbColour(0,0,0)],
            [matrix.rgbColour(0,0,0),   matrix.rgbColour(255,255,255), matrix.rgbColour(0,0,255),     matrix.rgbColour(0,0,0),   matrix.rgbColour(255,255,255), matrix.rgbColour(0,0,255),     matrix.rgbColour(0,0,0),    matrix.rgbColour(0,0,0)],
            [matrix.rgbColour(0,0,0),   matrix.rgbColour(255,0,0),     matrix.rgbColour(0,0,0),       matrix.rgbColour(0,0,0),   matrix.rgbColour(255,0,0),     matrix.rgbColour(0,0,0),       matrix.rgbColour(0,0,0),    matrix.rgbColour(0,0,0)],
            [matrix.rgbColour(0,0,0),   matrix.rgbColour(255,0,0),     matrix.rgbColour(0,0,0),       matrix.rgbColour(0,0,0),   matrix.rgbColour(255,0,0),     matrix.rgbColour(0,0,0),       matrix.rgbColour(0,0,0),    matrix.rgbColour(0,0,0)],
            [matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0),     matrix.rgbColour(255,0,0),     matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0),     matrix.rgbColour(0,0,0),       matrix.rgbColour(255,0,0),  matrix.rgbColour(255,0,0)],
            [matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0),     matrix.rgbColour(0,0,0),       matrix.rgbColour(0,0,0),   matrix.rgbColour(255,0,0),     matrix.rgbColour(255,0,0),     matrix.rgbColour(255,0,0),  matrix.rgbColour(0,0,0)],
            [matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0),     matrix.rgbColour(255,0,0),     matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0),     matrix.rgbColour(0,0,0),       matrix.rgbColour(0,0,0),    matrix.rgbColour(255,0,0)],
            [matrix.rgbColour(255,0,0), matrix.rgbColour(0,0,0),       matrix.rgbColour(255,0,0),     matrix.rgbColour(0,0,0),   matrix.rgbColour(255,0,0),     matrix.rgbColour(0,0,0),       matrix.rgbColour(0,0,0),    matrix.rgbColour(0,0,0)]]
    row = 0
    col = 0
    for r in T:
        for c in r:
            color = matrix.black()
            matrix.pixelSetXY(col, row, c)
            col += 1
            if (col > 7):
                col = 0
        row += 1
    matrix.pixelsShow()

def frog():
    print("frog")
    matrix.pixelsFill(matrix.black())
    T = [[matrix.rgbColour(0,0,0),   matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),   matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),    matrix.rgbColour(0,255,0),   matrix.rgbColour(0,255,0)],
         [matrix.rgbColour(0,0,0),   matrix.rgbColour(0,255,0),     matrix.rgbColour(0,0,0),       matrix.rgbColour(0,255,0),   matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),    matrix.rgbColour(0,0,0),     matrix.rgbColour(0,255,0)],
         [matrix.rgbColour(0,255,0), matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),   matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),    matrix.rgbColour(0,255,0),   matrix.rgbColour(0,255,0)],
         [matrix.rgbColour(0,255,0), matrix.rgbColour(0,0,0),       matrix.rgbColour(0,0,0),       matrix.rgbColour(0,0,0),     matrix.rgbColour(0,0,0),       matrix.rgbColour(0,0,0),      matrix.rgbColour(0,0,0),     matrix.rgbColour(0,0,0)],
         [matrix.rgbColour(0,255,0), matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),   matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),    matrix.rgbColour(0,255,0),   matrix.rgbColour(0,255,0)],
         [matrix.rgbColour(0,255,0), matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),   matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),    matrix.rgbColour(0,255,0),   matrix.rgbColour(0,255,0)],
         [matrix.rgbColour(0,255,0), matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),   matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),  matrix.rgbColour(0,255,0)],
         [matrix.rgbColour(0,255,0), matrix.rgbColour(0,255,0),     matrix.rgbColour(0,0,0),       matrix.rgbColour(0,255,0),   matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),     matrix.rgbColour(0,0,0),    matrix.rgbColour(0,255,0)]]
    row = 0
    col = 0
    for r in T:
        for c in r:
            color = matrix.black()
            matrix.pixelSetXY(col, row, c)
            col += 1
            if (col > 7):
                col = 0
        row += 1
    matrix.pixelsShow()

def bald():
    print("bald")
    matrix.pixelsFill(matrix.black())
    T = [[matrix.rgbColour(0,0,0),    matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),  matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),   matrix.rgbColour(0,0,0)],
         [matrix.rgbColour(68,59,49), matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),   matrix.rgbColour(68,59,49),     matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),     matrix.rgbColour(68,59,49)],
         [matrix.rgbColour(68,59,49), matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),   matrix.rgbColour(68,59,49),     matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),   matrix.rgbColour(68,59,49)],
         [matrix.rgbColour(68,59,49), matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),     matrix.rgbColour(68,59,49),       matrix.rgbColour(68,59,49),      matrix.rgbColour(68,59,49),     matrix.rgbColour(68,59,49)],
         [matrix.rgbColour(68,59,49), matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),   matrix.rgbColour(68,59,49),     matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),   matrix.rgbColour(68,59,49)],
         [matrix.rgbColour(100,100,100),    matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),   matrix.rgbColour(100,100,100),       matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),   matrix.rgbColour(68,59,49)],
         [matrix.rgbColour(68,59,49), matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),   matrix.rgbColour(68,59,49),     matrix.rgbColour(68,59,49),     matrix.rgbColour(68,59,49),  matrix.rgbColour(68,59,49)],
         [matrix.rgbColour(68,59,49), matrix.rgbColour(0,0,0),       matrix.rgbColour(0,0,0),       matrix.rgbColour(0,0,0),      matrix.rgbColour(68,59,49),     matrix.rgbColour(68,59,49),     matrix.rgbColour(68,59,49),    matrix.rgbColour(0,0,0)]]
    row = 0
    col = 0
    for r in T:
        for c in r:
            color = matrix.black()
            matrix.pixelSetXY(col, row, c)
            col += 1
            if (col > 7):
                col = 0
        row += 1
    matrix.pixelsShow()

def surprise():
    print("surprise")
    matrix.pixelsFill(matrix.black())
    T = [[matrix.rgbColour(150,70,0), matrix.rgbColour(150,70,0),    matrix.rgbColour(150,70,0),    matrix.rgbColour(150,70,0),  matrix.rgbColour(150,70,0),    matrix.rgbColour(150,70,0),    matrix.rgbColour(150,70,0),   matrix.rgbColour(150,70,0)],
         [matrix.rgbColour(68,59,49), matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),   matrix.rgbColour(68,59,49),     matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),     matrix.rgbColour(150,70,0)],
         [matrix.rgbColour(68,59,49), matrix.rgbColour(0,0,0),       matrix.rgbColour(100,100,100),    matrix.rgbColour(68,59,49),   matrix.rgbColour(0,0,0),     matrix.rgbColour(100,100,100),    matrix.rgbColour(68,59,49),   matrix.rgbColour(150,70,0)],
         [matrix.rgbColour(68,59,49), matrix.rgbColour(100,100,100), matrix.rgbColour(100,100,100),    matrix.rgbColour(68,59,49),     matrix.rgbColour(100,100,100),       matrix.rgbColour(100,100,100),      matrix.rgbColour(68,59,49),     matrix.rgbColour(150,70,0)],
         [matrix.rgbColour(68,59,49), matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),   matrix.rgbColour(68,59,49),     matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),   matrix.rgbColour(68,59,49)],
         [matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),    matrix.rgbColour(0,0,0),    matrix.rgbColour(0,0,0),   matrix.rgbColour(68,59,49),       matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),   matrix.rgbColour(68,59,49)],
         [matrix.rgbColour(68,59,49), matrix.rgbColour(68,59,49),    matrix.rgbColour(0,0,0),    matrix.rgbColour(0,0,0),   matrix.rgbColour(68,59,49),     matrix.rgbColour(68,59,49),     matrix.rgbColour(68,59,49),  matrix.rgbColour(150,70,0)],
         [matrix.rgbColour(0,0,0),    matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),       matrix.rgbColour(68,59,49),      matrix.rgbColour(68,59,49),     matrix.rgbColour(68,59,49),     matrix.rgbColour(68,59,49),    matrix.rgbColour(0,0,0)]]
    row = 0
    col = 0
    for r in T:
        for c in r:
            color = matrix.black()
            matrix.pixelSetXY(col, row, c)
            col += 1
            if (col > 7):
                col = 0
        row += 1
    matrix.pixelsShow()
