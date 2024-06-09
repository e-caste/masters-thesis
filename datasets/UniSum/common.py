import string

mitocw_dataset_file = "../subsets/mitocw_lectures_dataset/mitocw_lectures_dataset_clean.json"
yale_dataset_file = "../subsets/yale_lectures_dataset/yale_lectures_dataset_clean.json"
aggregated_dataset_file = "mitocw+yale_lectures_dataset.json"
extended_dataset_file = "mitocw+yale_extended_lectures_dataset.json"

train_split_csv_file = "train.csv"
dev_split_csv_file = "dev.csv"
test_split_csv_file = "test.csv"

train_split_extended_csv_file = "trainX.csv"
dev_split_extended_csv_file = "devX.csv"
test_split_extended_csv_file = "testX.csv"

test_split_testing_csv_file = "test_testing.csv"
other_split_testing_csv_file = "other_testing.csv"

_macrocategories = ["scientific", "humanities"]
macrocategories = {
    'Real Analysis': 'scientific',
    'Theory of Computation': 'scientific',
    'Psychology and Economics': 'humanities',
    'A 2020 Vision of Linear Algebra': 'scientific',
    'Graph Theory and Additive Combinatorics': 'scientific',
    'Laboratory Chemistry': 'scientific',
    'Machine Learning for Healthcare': 'scientific',
    'Introductory Biology': 'scientific',
    'Performance Engineering of Software Systems': 'scientific',
    'Matrix Methods in Data Analysis, Signal Processing, and Machine Learning': 'scientific',
    'Innovation Systems for Science, Technology, Energy, Manufacturing, and Health': 'scientific',
    'Introduction to Nuclear Engineering and Ionizing Radiation': 'scientific',
    'Learn Differential Equations: Up Close with Gilbert Strang and Cleve Moler': 'scientific',
    'Brains, Minds and Machines Summer Course': 'scientific',
    'Systems Biology': 'scientific',
    'String Theory and Holographic Duality': 'scientific',
    'Green Supply Chain Management': 'scientific',
    'Foundations of Computational and Systems Biology': 'scientific',
    'Fundamentals of Photovoltaics': 'scientific',
    'The Film Experience': 'humanities',
    'Sensory Systems': 'scientific',
    'The Battlecode Programming Competition': 'scientific',
    'Introduction to EECS II: Digital Communication Systems': 'scientific',
    'Introduction to Lean Six Sigma Methods': 'scientific',
    'Energy Decisions, Markets, and Policies': 'humanities',
    'Signals and Systems': 'scientific',
    'Calculus Revisited: Complex Variables, Differential Equations, and Linear Algebra': 'scientific',
    'Calculus Revisited: Multivariable Calculus': 'scientific',
    'Discrete Stochastic Processes': 'scientific',
    'Artificial Intelligence': 'scientific',
    'Linear Algebra': 'scientific',
    'Power and Politics in Today’s World': 'humanities',
    'Modern Poetry with Langdon Hammer  (ENGL 310)': 'humanities',
    'Introduction to the Old Testament With Christine Hayes': 'humanities',
    'American History: From Emancipation to the Present': 'humanities',
    'Listening to Music with Craig Wright': 'humanities',
    'Timothy Snyder: The Making of Modern Ukraine': 'humanities',
    'Philosophy and the Science of Human Nature w/ Tamar Gendler': 'humanities',
    "Yale University's Lectures: The Early Middle Ages, 284-1000": 'humanities',
    'Hemingway, Fitzgerald, Faulkner with Wai Chee Dimock': 'humanities',
    "Cervantes' Don Quixote with Roberto González Echevarría": 'humanities',
    'Foundations of Modern Social Theory with Iván Szelényi': 'humanities',
    'Capitalism: Success, Crisis and Reform with Douglas W. Rae': 'humanities',
    'The Moral Foundations of Politics with Ian Shapiro': 'humanities',
    'Fundamentals of Physics II with Ramamurti Shankar': 'scientific',
    'Early Modern England with Keith E. Wrightson': 'humanities',
    'Epidemics in Western Society Since 1600 with Frank Snowden': 'humanities',
    'The American Revolution with Joanne B. Freeman': 'humanities',
    'Environmental Politics and Law with John Wargo': 'humanities',
    'Financial Theory with John Geanakoplos': 'humanities',
    'Global Problems of Population Growth with Robert Wyman': 'humanities',
    'Dante in Translation with Giuseppe Mazzotta': 'humanities',
    'Roman Architecture with Diana E. E. Kleiner': 'humanities',
    'European Civiliization (1648-1945) with John Merriman': 'humanities',
    'Introduction to Theory of Literature with Paul H. Fry': 'humanities',
    'Evolution, Ecology and Behavior with Stephen C. Stearns': 'humanities',
    'The Civil War and Reconstruction with David Blight': 'humanities',
    'The American Novel Since 1945 with Amy Hungerford': 'humanities',
    'Game Theory with Ben Polak': 'scientific',
    'Introduction to Ancient Greek History with Donald Kagan': 'humanities',
    'Frontiers of Biomedical Engineering with W. Mark Saltzman': 'scientific',
    'Financial Markets (2008) with Robert Shiller': 'humanities',
    'Introduction to Psychology with Paul Bloom': 'humanities',
    'Death with Shelly Kagan': 'humanities',
    'Frontiers/Controversies in Astrophysics with Charles Bailyn': 'scientific',
    'Introduction to Political Philosophy with Steven B. Smith': 'humanities',
    'Fundamentals of Physics with Ramamurti Shankar': 'scientific'
}

_categories = ["mathematics", "physics", "computer science", "economics", "literature", "history", "philosophy", "arts", "biology", "chemistry", "engineering", "business", "politics", "social studies", "psychology"]
categories = {
    'Real Analysis': 'mathematics',
    'Theory of Computation': 'computer science',
    'Psychology and Economics': 'economics',
    'A 2020 Vision of Linear Algebra': 'mathematics',
    'Graph Theory and Additive Combinatorics': 'mathematics',
    'Laboratory Chemistry': 'chemistry',
    'Machine Learning for Healthcare': 'computer science',
    'Introductory Biology': 'biology',
    'Performance Engineering of Software Systems': 'computer science',
    'Matrix Methods in Data Analysis, Signal Processing, and Machine Learning': 'mathematics',
    'Innovation Systems for Science, Technology, Energy, Manufacturing, and Health': 'engineering',
    'Introduction to Nuclear Engineering and Ionizing Radiation': 'physics',
    'Learn Differential Equations: Up Close with Gilbert Strang and Cleve Moler': 'mathematics',
    'Brains, Minds and Machines Summer Course': 'computer science',
    'Systems Biology': 'biology',
    'String Theory and Holographic Duality': 'physics',
    'Green Supply Chain Management': 'business',
    'Foundations of Computational and Systems Biology': 'biology',
    'Fundamentals of Photovoltaics': 'engineering',
    'The Film Experience': 'arts',
    'Sensory Systems': 'biology',
    'The Battlecode Programming Competition': 'computer science',
    'Introduction to EECS II: Digital Communication Systems': 'computer science',
    'Introduction to Lean Six Sigma Methods': 'business',
    'Energy Decisions, Markets, and Policies': 'engineering',
    'Signals and Systems': 'engineering',
    'Calculus Revisited: Complex Variables, Differential Equations, and Linear Algebra': 'mathematics',
    'Calculus Revisited: Multivariable Calculus': 'mathematics',
    'Discrete Stochastic Processes': 'mathematics',
    'Artificial Intelligence': 'computer science',
    'Linear Algebra': 'mathematics',
    'Power and Politics in Today’s World': 'politics',
    'Modern Poetry with Langdon Hammer  (ENGL 310)': 'literature',
    'Introduction to the Old Testament With Christine Hayes': 'literature',
    'American History: From Emancipation to the Present': 'history',
    'Listening to Music with Craig Wright': 'arts',
    'Timothy Snyder: The Making of Modern Ukraine': 'history',
    'Philosophy and the Science of Human Nature w/ Tamar Gendler': 'philosophy',
    "Yale University's Lectures: The Early Middle Ages, 284-1000": 'history',
    'Hemingway, Fitzgerald, Faulkner with Wai Chee Dimock': 'literature',
    "Cervantes' Don Quixote with Roberto González Echevarría": 'literature',
    'Foundations of Modern Social Theory with Iván Szelényi': 'social studies',
    'Capitalism: Success, Crisis and Reform with Douglas W. Rae': 'economics',
    'The Moral Foundations of Politics with Ian Shapiro': 'philosophy',
    'Fundamentals of Physics II with Ramamurti Shankar': 'physics',
    'Early Modern England with Keith E. Wrightson': 'history',
    'Epidemics in Western Society Since 1600 with Frank Snowden': 'history',
    'The American Revolution with Joanne B. Freeman': 'history',
    'Environmental Politics and Law with John Wargo': 'politics',
    'Financial Theory with John Geanakoplos': 'economics',
    'Global Problems of Population Growth with Robert Wyman': 'social studies',
    'Dante in Translation with Giuseppe Mazzotta': 'literature',
    'Roman Architecture with Diana E. E. Kleiner': 'history',
    'European Civiliization (1648-1945) with John Merriman': 'history',
    'Introduction to Theory of Literature with Paul H. Fry': 'literature',
    'Evolution, Ecology and Behavior with Stephen C. Stearns': 'social studies',
    'The Civil War and Reconstruction with David Blight': 'history',
    'The American Novel Since 1945 with Amy Hungerford': 'literature',
    'Game Theory with Ben Polak': 'computer science',
    'Introduction to Ancient Greek History with Donald Kagan': 'history',
    'Frontiers of Biomedical Engineering with W. Mark Saltzman': 'engineering',
    'Financial Markets (2008) with Robert Shiller': 'economics',
    'Introduction to Psychology with Paul Bloom': 'psychology',
    'Death with Shelly Kagan': 'philosophy',
    'Frontiers/Controversies in Astrophysics with Charles Bailyn': 'physics',
    'Introduction to Political Philosophy with Steven B. Smith': 'philosophy',
    'Fundamentals of Physics with Ramamurti Shankar': 'physics'
}


def sanitize_lecture_name(name: str) -> str:
    """given the title for a lecture, return a sanitized version that is filesystem friendly"""
    result = ""
    for character in name:
        if character in string.ascii_letters or character in string.digits:
            result += character
        elif character == "&":
            result += "and"
        elif character in "()[]{}":
            result += "+"
        else:
            result += "-"
    return result
