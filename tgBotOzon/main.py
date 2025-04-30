import os, sys
os.chdir( os.path.abspath( os.path.dirname( os.path.dirname(__file__) ) ) )
sys.path.append( os.getcwd() )

def main():
    print('hello', os.getcwd())
    pass

if __name__ == '__main__':
    main()